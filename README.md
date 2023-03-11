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
$ mamba create -n aialbum transformers python=3.10 pytorch fairscale dask-mongo torchaudio pytorch-cuda=11.7 iopath cudatoolkit=11.7  -c pytorch -c nvidia -c iopath -c conda-forge
$ mamba install rapids=23.02 -c rapidsai -c conda-forge -c nvidia 
$ pip install "fastapi[all]" pillow pillow-heif einops spacy pycocoevalcap cryptography==38.0.4 motor pymongo pyyaml networkx omegaconf timm decord opencv-python webdataset jupyterlab torchvision
$ pip install tensorflow
$ pip install gdown
```

### post install

```bash
$ python -m spacy download en_core_web_sm
$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
```
### Building DLIB library

```bash
./build.sh
```

## Running the dev server

```
uvicorn server.__main__:app --reload
```

## Deployment

```
python -m server
```