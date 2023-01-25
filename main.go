package main

import (
	"log"
	"math/rand"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/commands"
	"github.com/diraven/traveller/state"
)

var s *discordgo.Session

func main() {
	rand.Seed(time.Now().Unix())
	var err error

	// Create session.
	s, err := discordgo.New("Bot " + os.Getenv("DISCORD_BOT_TOKEN"))
	if err != nil {
		log.Fatalf("Invalid bot parameters: %v", err)
	}

	// Handle state.
	defer state.State.Save()

	// Open session.
	s.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		log.Printf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator)
	})
	err = s.Open()
	if err != nil {
		log.Fatalf("Cannot open the session: %v", err)
	}
	defer s.Close()

	// Initialize commands.
	commands.Init(s)
	defer commands.DeInit(s)

	// Wait for os.Interrupt.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, os.Kill, syscall.SIGTERM, syscall.SIGINT)
	log.Println("Press Ctrl+C to exit.")
	<-stop
	log.Println("Gracefully shutting down.")
}
