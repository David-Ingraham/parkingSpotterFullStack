
import asyncio, httpx, time
from app.config import get_settings
from app.inference import OpenParkingDetector
from app.notifier import send_open_parking_email
from app.worker import _caption_image

async def main():
    s = get_settings()
    det = OpenParkingDetector(s)
    det.load()
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f'{s.dot_image_base}/a3058350-1552-459f-8379-2fd06895e70a/image', params={'t': int(time.time()*1000)})
        r.raise_for_status()
    status, annotated = det.predict(r.content)
    print('status:', status, 'annotated bytes:', len(annotated) if annotated else None)
    frame = annotated or r.content
    captioned = _caption_image(frame, 'Delancey St & Bowery (TEST)')
    ok = await send_open_parking_email(
        s,
        to_email='davidingrahamf@gmail.com',
        address='Delancey_St_Bowery_St',
        display='Delancey St & Bowery (TEST)',
        image_bytes=captioned,
    )
    print('sent:', ok)

asyncio.run(main())

