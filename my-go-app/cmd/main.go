package main

import (
    "my-go-app/internal/app"
    "log"
)

func main() {
    application := app.App{}

    if err := application.Start(); err != nil {
        log.Fatalf("Failed to start the application: %v", err)
    }

    // Application logic goes here

    defer application.Stop()
}