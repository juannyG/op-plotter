FROM python:3.8-slim-buster AS build

RUN apt-get update
#RUN apt-get -y install gcc git g++

RUN pip install matplotlib ipython

FROM python:3.8-slim-buster
COPY --from=build /usr /usr

WORKDIR /app
COPY . ./
CMD ["tail", "-f", "/dev/null"]