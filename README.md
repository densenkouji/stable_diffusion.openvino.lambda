# stable_diffusion.openvino.lamda

Implementation of Text-To-Image generation using Stable Diffusion on AWS Lambda(x86_64).
<p align="center">
  <img src="data/title.png"/>
</p>

```
This project is based on the "stable_diffusion.openvino" project and ported to AWS Lambda.
https://github.com/bes-dev/stable_diffusion.openvino
```

## Requirements

* AWS Lambda(x86_64)
* Python 3.9

## Installation Instructions
### 1. Installing AWS CLI & Docker
Install AWS CLI and Docker.
- AWS CLI
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

- Docker
https://docs.docker.com/engine/install/

### 2. Config AWS CLI
Input AWS Access Key ID, AWS Secret Access Key, Default region name
```bash
$ aws configure
AWS Access Key ID [None]: YOUR ACCESSKEY
AWS Secret Access Key [None]: YOUR SECRETKEY
Default region name [None]: YOUR REGION (ex.us-east-1)
Default output format [None]:
```

### 3. Clone Project
```bash
$ git clone https://github.com/densenkouji/stable_diffusion.openvino.lambda.git
$ cd stable_diffusion.openvino.lambda
```

### 4. Install
```bash:
$ sh ./install.sh
(Create New) Input AWS Lambda Function Name [ex.mySdFunction]: YOUR LAMBDA FUNCTION NAME
```
Results
```bash
TRACINGCONFIG   PassThrough
******* Complete!! *******
The following resources were created.
- Lmabda function: mySdFunction-yty7mdazmzzlywey
- Role: mySdFunction-yty7mdazmzzlywey-role
- ECR Repository: mysdfunction-yty7mdazmzzlywey-repo
- S3 Bucket: mysdfunction-yty7mdazmzzlywey-bucket
```

### 5. Test(Text-To-Image)

```bash
$ aws lambda invoke \
   --function-name mySdFunction-yty7mdazmzzlywey \
   --invocation-type 'RequestResponse' \
   --payload '{"prompt":"Street-art painting of Tower in style of Banksy"}' \
   --cli-read-timeout 600 \
   --cli-binary-format raw-in-base64-out \
   output.text
```

## Generate image from text description

```bash
usage: 
{
  "prompt": "Street-art painting of Tower in style of Banksy"
}

optional arguments:
  lambda              lambda function name
  seed                random seed for generating consistent images per prompt
  beta_start          LMSDiscreteScheduler::beta_start
  beta_end            LMSDiscreteScheduler::beta_end
  beta_schedule       LMSDiscreteScheduler::beta_schedule
  num_inference_steps num inference steps
  guidance_scale      guidance scale
  eta                 eta
  prompt              prompt
  init_image          filename to initial image (S3)
  strength            how strong the initial image should be noised [0.0, 1.0]
  mask                mask of the region to inpaint on the initial image
  output              prefix output image name
  n                   Loop count
  limit               Loop limit
```

## Examples

### Example Text-To-Image
```bash
python demo.py --lambda myFunc1-emrzmjvlngu9mwiw --n 5 --prompt "Street-art painting of Sakura with tower in style of Banksy"
```

### Example Image-To-Image
```bash
python demo.py --lambda myFunc1-emrzmjvlngu9mwiw --prompt "Street-art painting of Sakura with tower in style of Banksy" --init_image input.png --strength 0.5
```

## Acknowledgements
* stable_diffusion.openvino: https://github.com/bes-dev/stable_diffusion.openvino
* Original implementation of Stable Diffusion: https://github.com/CompVis/stable-diffusion
* diffusers library: https://github.com/huggingface/diffusers

## Disclaimer

The authors are not responsible for the content generated using this project.
Please, don't use this project to produce illegal, harmful, offensive etc. content.
