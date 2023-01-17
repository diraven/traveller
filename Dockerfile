FROM golang:1.19-alpine as build

WORKDIR /app
COPY go.mod ./
COPY go.sum ./
RUN go mod download
COPY . ./
RUN go build -o traveller

## Deploy
FROM gcr.io/distroless/base-debian10

WORKDIR /app
COPY --from=build /app/traveller traveller

USER nonroot:nonroot
ENTRYPOINT ["traveller"]
