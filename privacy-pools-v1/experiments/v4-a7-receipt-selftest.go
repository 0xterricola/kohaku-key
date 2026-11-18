package main

import (
	"fmt"
	"os"
)

func main() {
	if err := selfTest(); err != nil {
		fmt.Fprintln(os.Stderr, "FAIL:", err)
		os.Exit(1)
	}
}
