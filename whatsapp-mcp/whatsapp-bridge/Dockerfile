FROM golang:1.24

WORKDIR /app

COPY . .

WORKDIR /app/whatsapp-bridge

RUN go mod download

CMD ["go", "run", "main.go"]
