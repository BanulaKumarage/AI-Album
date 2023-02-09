import pathlib
import logging
from threading import Thread

from PIL import Image
import torch
from lavis.models import load_model_and_preprocess

from server.db import media
from server.conf import captioning_workers_per_gpu


LOG = logging.getLogger(__name__)


def captioning_worker(dir, workers: int, worker_id: int, device_name: str):
    model, vis_processors, _ = load_model_and_preprocess(name="blip_caption", model_type="base_coco", is_eval=True, device=device_name)
    processed = 0

    for n, entry in enumerate(media.get_media_sync(
        { 
            '$and': [                
                # { 'caption': { '$exists': False } },
                { 'path': { '$regex': 'jpg$|JPG$|JPEG$|jpeg$' } }
            ]
        }, 
        {
            '_id': 1,
            'path': 1
        },
        'name', 0, 0)
        ):

        if kill_me.is_set():
            LOG.debug(f'WORKER killed')
            return

        if n % workers == worker_id:
            processed += 1
            path = str(pathlib.Path().joinpath(dir, 'data', entry['path']))
            raw_image = Image.open(path).convert("RGB")
            image = vis_processors["eval"](raw_image).unsqueeze(0).to(device_name)
            captions = model.generate({"image": image}, use_nucleus_sampling=True, num_captions=5)
            media.update_media_sync(
                { '_id':  entry['_id'] }, 
                { '$set':  { 'caption': '\n'.join([caption.capitalize() for caption in captions])}}
            )
    LOG.debug(f'WORKER {worker_id} proceessed {processed} images')


def run_image_processing(dir):
    device_count = torch.cuda.device_count()
    
    if device_count > 0:
        threads = []
        workers_per_gpu = captioning_workers_per_gpu
        workers = workers_per_gpu * device_count

        LOG.debug(f'Start image processing using {[f"device:{idx}" for idx in range(device_count)]}')
        
        for device_id in range(device_count):
            device_name = f'cuda:{device_id}'

            for worker in range(workers_per_gpu):
                worker_id = device_id * workers_per_gpu + worker
                thread = Thread(target=captioning_worker, args=(dir, workers, worker_id, device_name))
                threads.append(thread)
        
        LOG.debug(f'Running {workers} captioning workers')
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        LOG.debug(f'Captioning complete')
    else:
        LOG.debug('CUDA not found!')
        LOG.debug(f'Running 1 captioning workers')
        captioning_worker(1, 1, 'cpu')
        LOG.debug(f'Captioning complete')
