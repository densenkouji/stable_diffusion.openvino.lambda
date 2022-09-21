FROM public.ecr.aws/lambda/python:3.9 as builder
COPY openvino-2022.repo /etc/yum.repos.d
RUN yum -y update && yum -y install openvino-2022.1.0 gcc make gcc-c++ zlib-devel bison bison-devel gzip glibc-static wget tar git
RUN wget https://ftp.gnu.org/gnu/glibc/glibc-2.27.tar.gz && tar zxvf glibc-2.27.tar.gz && rm glibc-2.27.tar.gz && mv ./glibc-2.27/ /opt/glibc-2.27/
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | bash
RUN yum install -y git-lfs && git lfs install && git clone https://huggingface.co/bes-dev/stable-diffusion-v1-4-openvino
ENV GIT_LFS_SKIP_SMUDGE=1
RUN git clone https://huggingface.co/openai/clip-vit-large-patch14
WORKDIR /opt/glibc-2.27/build
RUN /opt/glibc-2.27/configure --prefix=/var/task
RUN make && make install

FROM public.ecr.aws/lambda/python:3.9 as production
COPY requirements.txt  ./
RUN pip install -r requirements.txt
RUN yum -y update && yum -y install mesa-libGL
# model
COPY --from=builder \
    /var/task/stable-diffusion-v1-4-openvino/text_encoder.bin \
    /var/task/stable-diffusion-v1-4-openvino/text_encoder.xml \
    /var/task/stable-diffusion-v1-4-openvino/unet.bin \
    /var/task/stable-diffusion-v1-4-openvino/unet.xml \
    /var/task/stable-diffusion-v1-4-openvino/vae_decoder.bin \
    /var/task/stable-diffusion-v1-4-openvino/vae_decoder.xml \
    /var/task/stable-diffusion-v1-4-openvino/vae_encoder.bin \
    /var/task/stable-diffusion-v1-4-openvino/vae_encoder.xml /var/task/model/
# tokenizer
COPY --from=builder \
    /var/task/clip-vit-large-patch14/tokenizer_config.json \
    /var/task/clip-vit-large-patch14/vocab.json \
    /var/task/clip-vit-large-patch14/merges.txt \
    /var/task/clip-vit-large-patch14/special_tokens_map.json \
    /var/task/clip-vit-large-patch14/tokenizer.json /var/task/tokenizer/

COPY --from=builder /opt/intel/openvino_2022/runtime/lib/intel64/* /var/task/
COPY --from=builder /opt/intel/openvino_2022/runtime/3rdparty/tbb/lib/* /var/task/
COPY --from=builder /opt/intel/openvino_2022/python/python3.9/ /var/task/python3.9/
COPY --from=builder /var/task/lib/libm.so.6 /lib64/

COPY app.py ./
COPY stable_diffusion_engine.py ./
CMD [ "app.handler" ]