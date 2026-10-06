import asyncio
from src.inference_control_plane.core.config import Settings
from src.inference_control_plane.services.llm_client import generate_completion, init_http_client, close_http_client

async def main():
    settings = Settings()
    init_http_client(settings)
    try:
        model, text = await generate_completion(
            settings,
            prompt="Say hello",
            model_tier="cheap",
        )
        print("Success:", text.encode('ascii', 'ignore').decode('ascii'))
    except Exception as e:
        print("EXCEPTION:", e)
    finally:
        await close_http_client()

if __name__ == "__main__":
    asyncio.run(main())
