import asyncio
import json
import logging
import websockets
from typing import Optional

# Importamos el molde del Arquitecto
try:
    from app.domain.schemas import Candle
except ImportError:
    # Fallback para pruebas aisladas si no se encuentra el módulo
    from pydantic import BaseModel, ConfigDict
    class Candle(BaseModel):
        timestamp: int
        open: float
        high: float
        low: float
        close: float
        volume: float
        symbol: str
        model_config = ConfigDict(frozen=True)

# Configuración
WS_URL = "wss://api.hyperliquid-testnet.xyz/ws"
TARGET_COIN = "ETH"
TIMEFRAME = "1m"

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

# Logging Config
logger = logging.getLogger("HyperliquidConnector")

class HyperliquidStream:
    def __init__(self, on_candle=None, on_user_event=None):
        self.ws_url = WS_URL
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
        self.running = False
        self.user_address = PUBLIC_ADDRESS
        self.on_candle = on_candle
        self.on_user_event = on_user_event

    async def connect(self):
        self.running = True
        while self.running:
            try:
                logger.info(f"Iniciando conexión a {self.ws_url}...")
                async with websockets.connect(self.ws_url) as ws:
                    self.reconnect_delay = 1  # Reset backoff on success
                    logger.info("Conexión WebSocket establecida.")
                    
                    # 1. Suscripción al canal de velas
                    subscribe_candle = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "candle",
                            "coin": TARGET_COIN,
                            "interval": TIMEFRAME
                        }
                    }
                    await ws.send(json.dumps(subscribe_candle))
                    logger.info(f"Suscrito a {TARGET_COIN} [{TIMEFRAME}]")

                    # 2. Suscripción al canal de usuario (si hay dirección)
                    if self.user_address:
                        subscribe_user = {
                            "method": "subscribe",
                            "subscription": {
                                "type": "userEvents",
                                "user": self.user_address
                            }
                        }
                        await ws.send(json.dumps(subscribe_user))
                        logger.info(f"Suscrito a UserEvents para {self.user_address[:8]}...")
                    else:
                        logger.warning("PUBLIC_ADDRESS no configurada. No se recibirán eventos de usuario.")

                    async for message in ws:
                        if not self.running:
                            break
                        await self.process_message(message)

            except (websockets.ConnectionClosed, asyncio.TimeoutError, OSError) as e:
                logger.warning(f"Conexión perdida ({type(e).__name__}). Reintentando en {self.reconnect_delay}s...")
                if self.running:
                    await asyncio.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            
            except Exception as e:
                logger.exception(f"Error crítico no manejado: {e}")
                if self.running:
                    await asyncio.sleep(5)

    def stop(self):
        self.running = False

    async def process_message(self, raw_msg: str):
        try:
            data = json.loads(raw_msg)
            
            # Ignorar mensajes de confirmación de suscripción
            if data.get("channel") == "subscriptionResponse":
                return

            channel = data.get("channel")

            if channel == "candle":
                candle_raw = data.get("data")
                if candle_raw:
                    # NORMALIZACIÓN DE DATOS
                    candle = Candle(
                        timestamp=candle_raw['t'],
                        open=float(candle_raw['o']),
                        high=float(candle_raw['h']),
                        low=float(candle_raw['l']),
                        close=float(candle_raw['c']),
                        volume=float(candle_raw['v']),
                        symbol=candle_raw['s']
                    )
                    
                    logger.info(f"CEMENTO VERTIDO >> {candle}")
                    if self.on_candle:
                        if asyncio.iscoroutinefunction(self.on_candle):
                            await self.on_candle(candle)
                        else:
                            self.on_candle(candle)
            
            elif channel == "user":
                user_data = data.get("data")
                # Aquí procesaríamos fills, funding updates, etc.
                # Por ahora solo logueamos para validar la conexión autenticada
                logger.info(f"USER EVENT >> {user_data}")
                if self.on_user_event:
                    if asyncio.iscoroutinefunction(self.on_user_event):
                        await self.on_user_event(user_data)
                    else:
                        self.on_user_event(user_data)

        except json.JSONDecodeError:
            logger.error("Error decodificando JSON de Hyperliquid")
        except KeyError as e:
            logger.error(f"Estructura de datos inesperada, falta campo: {e}")
        except ValueError as e:
            logger.error(f"Error de tipo de datos: {e}")

if __name__ == "__main__":
    # Configuración básica de logging para ejecución directa
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [API_SPEC] - %(levelname)s - %(message)s'
    )
    stream = HyperliquidStream()
    try:
        asyncio.run(stream.connect())
    except KeyboardInterrupt:
        logger.info("Deteniendo conector por solicitud del usuario.")
