# -- coding: utf-8 --`
import argparse
import json
import botocore
import boto3
 
def main(args):
    cfg = botocore.config.Config(retries={'max_attempts': 0}, read_timeout=900, connect_timeout=900)
    args = {k: v for k, v in args.items() if v is not None}

    try:
        lambda_client = boto3.client('lambda', config=cfg)
        s3_resource = boto3.resource('s3')
        results = {}

        for num in range(args['n']):
            response = lambda_client.invoke(
                FunctionName=args['lambda'],
                InvocationType='RequestResponse',
                Payload=json.dumps(args)
                )

            json_dict = json.loads(response['Payload'].read().decode('utf-8'))

            if json_dict['statusCode'] == 200:
                s3_resource.Bucket(json_dict['body']['bucket']).download_file(json_dict['body']['output'], json_dict['body']['output'])
            else:
                break
            results[num] = json_dict

        print(json.dumps(results, indent=2))

    except Exception as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Lambda Functionn
    parser.add_argument("--lambda", type=str, required=True, help="Lambda Function Name")
    # randomizer params
    parser.add_argument("--seed", type=int, default=None, help="random seed for generating consistent images per prompt")
    # scheduler params
    parser.add_argument("--beta-start", type=float, default=None, help="LMSDiscreteScheduler::beta_start")
    parser.add_argument("--beta-end", type=float, default=None, help="LMSDiscreteScheduler::beta_end")
    parser.add_argument("--beta-schedule", type=str, default=None, help="LMSDiscreteScheduler::beta_schedule")
    # diffusion params
    parser.add_argument("--num-inference-steps", type=int, default=None, help="num inference steps")
    parser.add_argument("--guidance-scale", type=float, default=None, help="guidance scale")
    parser.add_argument("--eta", type=float, default=None, help="eta")
    # prompt
    parser.add_argument("--prompt", type=str, default="Street-art painting of Tower in style of Banksy, photorealism", help="prompt")
    # img2img params
    parser.add_argument("--init-image", type=str, default=None, help="path to initial image")
    parser.add_argument("--strength", type=float, default=None, help="how strong the initial image should be noised [0.0, 1.0]")
    # inpainting
    parser.add_argument("--mask", type=str, default=None, help="mask of the region to inpaint on the initial image")
    # output name
    parser.add_argument("--output", type=str, default=None, help="output image prefix")
    # loop
    parser.add_argument("--n", type=int, default=1, help="Loop Count")
 
    main(vars(parser.parse_args()))
