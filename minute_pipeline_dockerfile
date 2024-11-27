FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip3 install -r requirements.txt

COPY pipeline/extract.py ${LAMBDA_TASK_ROOT}

COPY pipeline/load.py ${LAMBDA_TASK_ROOT}

COPY pipeline/transform.py ${LAMBDA_TASK_ROOT}

COPY pipeline/pipeline.py ${LAMBDA_TASK_ROOT}

CMD [ "pipeline.lambda_handler" ]