# AI-Album

Hobby project in progress. Everything is still in progress. Re-use at your own risk!

### Implemented features
    - Image indexing (recursive album creation and loading to database)
    - Image captioning with multiple GPUs

### Upcoming features
    - Image face annotation
    - Face index


![Image](assets/test.png)

## Dependencies

### python dependencies

```bash
$ pip install aiohttp
$ pip install aiohttp[speedups]
$ pip install aiohttp-devtools
$ pip install pymongo
$ pip install pydantic-mongo
$ pip install jsons
$ pip ninstall pyyaml
$ pip install networkx
$ mamba install pytorch torchvision cudnn torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
$ pip install cryptography==38.0.4
$ pip install aiohttp_cors
```

### Building DLIB library

```bash
./build.sh
```

## Running the dev server

```
adev runserver server/__main__.py
```

## Deployment

```
python -m server
```