package main

import (
	"fmt"
	"os/exec"
)

func main() {
	fmt.Println("☁️ Azür Sync: Starting Alibaba upload...")

	cmd := exec.Command("ossutil64", "cp", "-r", "~/SoulCoreHub/", "oss://kinfolk-backup/")
	err := cmd.Run()
	if err != nil {
		fmt.Println("❌ Sync failed:", err)
		return
	}

	fmt.Println("✅ Cloud sync complete.")
}
