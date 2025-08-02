package pkg

import (
    "log"
    "os"
)

// Log is a utility function to log messages to the console.
func Log(message string) {
    log.Println(message)
}

// HandleError is a utility function to handle errors gracefully.
func HandleError(err error) {
    if err != nil {
        log.Fatalf("Error: %v", err)
        os.Exit(1)
    }
}