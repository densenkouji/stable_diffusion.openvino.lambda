# -- coding: utf-8 --`
import os
import gc
from datetime import datetime
import numpy as np
# engine
from stable_diffusion_engine import StableDiffusionEngine
from diffusers import LMSDiscreteScheduler, PNDMScheduler # scheduler
import cv2
import boto3

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

# S3 Bucket Name
BUCKET_NAME = os.environ['BUCKET']

# DEFAULT_MODEL = "bes-dev/stable-diffusion-v1-4-openvino"  # model name
# DEFAULT_TOKENIZER = "openai/clip-vit-large-patch14"  # tokenizer
DEFAULT_SEED = None # random seed for generating consistent images per prompt
DEFAULT_BETA_START = 0.00085  # LMSDiscreteScheduler::beta_start
DEFAULT_BETA_END = 0.012  # LMSDiscreteScheduler::beta_end
DEFAULT_BETA_SCHEDULE = "scaled_linear"  # LMSDiscreteScheduler::beta_schedule
DEFAULT_NUM_INFERENCE_STEPS = 32  # num inference steps
DEFAULT_GUIDANCE_SCALE = 7.5  # guidance scale
DEFAULT_ETA = 0.0  # eta
DEFAULT_PROMPT = "Street-art painting of Sakura with tower in style of Banksy"  # prompt
DEFAULT_INIT_IMAGE = None  # path to initial image
DEFAULT_STRENGTH = 0.5 # how strong the initial image should be noised [0.0, 1.0]
DEFAULT_MASK = None  # mask of the region to inpaint on the initial image
DEFAULT_OUTPUT = "output"  # output image name

def file_exists_s3(filename):
    try:
        result = s3_client.list_objects(Bucket=BUCKET_NAME, Prefix=filename )["Contents"]
        if len(result) > 0:
           return True
        else:
           return False
    except:
        return False

def download_file_s3(file_from, save_to):
    if file_exists_s3(file_from):
        try:
            s3_resource.Bucket(BUCKET_NAME).download_file(file_from, '/tmp/' + save_to)
            return True
        except:
            return False
    else:
        return False

def handler(event, context):
    if event.setdefault('seed', DEFAULT_SEED) is not None:
        np.random.seed(event['seed'])
    if event.setdefault('init_image', DEFAULT_INIT_IMAGE) is None:
        scheduler = LMSDiscreteScheduler(
            beta_start=event.setdefault('beta_start', DEFAULT_BETA_START),
            beta_end=event.setdefault('beta_end', DEFAULT_BETA_END),
            beta_schedule=event.setdefault('beta_schedule', DEFAULT_BETA_SCHEDULE),
            tensor_format="np"
        )
    else:
        scheduler = PNDMScheduler(
            beta_start=event.setdefault('beta_start', DEFAULT_BETA_START),
            beta_end=event.setdefault('beta_end', DEFAULT_BETA_END),
            beta_schedule=event.setdefault('beta_schedule', DEFAULT_BETA_SCHEDULE),
            skip_prk_steps = True,
            tensor_format="np"
        )
        download_file_s3(event.setdefault('init_image', DEFAULT_INIT_IMAGE), event.setdefault('init_image', DEFAULT_INIT_IMAGE))
        if event.setdefault('mask', DEFAULT_MASK) is not None:
            download_file_s3(event.setdefault('mask', DEFAULT_MASK), event.setdefault('mask', DEFAULT_MASK))
    engine = StableDiffusionEngine(
        scheduler = scheduler
        # model = event.setdefault('model', DEFAULT_MODEL),
        # tokenizer = event.setdefault('tokenizer', DEFAULT_TOKENIZER)
    )
    image = engine(
        prompt = event.setdefault('prompt', DEFAULT_PROMPT),
        init_image = None if event.setdefault('init_image', DEFAULT_INIT_IMAGE) is None else cv2.imread('/tmp/' + event.setdefault('init_image', DEFAULT_INIT_IMAGE)),
        mask = None if event.setdefault('mask', DEFAULT_MASK) is None else cv2.imread('/tmp/' + event.setdefault('mask', DEFAULT_MASK), 0),
        strength = event.setdefault('strength', DEFAULT_STRENGTH),
        num_inference_steps = event.setdefault('num_inference_steps', DEFAULT_NUM_INFERENCE_STEPS),
        guidance_scale = event.setdefault('guidance_scale', DEFAULT_GUIDANCE_SCALE),
        eta = event.setdefault('eta', DEFAULT_ETA)
    )
    del engine

    output_img = event.setdefault('output', 'sd') + '_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png'
    cv2.imwrite('/tmp/' + output_img , image)

    bucket = s3_resource.Bucket(BUCKET_NAME)
    bucket.upload_file('/tmp/' + output_img, output_img)
    gc.collect()

    return  {"statusCode": 200, "body": {"output": output_img}}