package main

import (
	"log"
	"os"
	"os/signal"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/commands"
	"github.com/diraven/traveller/state"
)

var s *discordgo.Session

func main() {
	var err error

	// Create session.
	s, err := discordgo.New("Bot " + os.Getenv("DISCORD_BOT_TOKEN"))
	if err != nil {
		log.Fatalf("Invalid bot parameters: %v", err)
	}

	// Open session.
	s.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		log.Printf("Logged in as: %v#%v", s.State.User.Username, s.State.User.Discriminator)
	})
	err = s.Open()
	if err != nil {
		log.Fatalf("Cannot open the session: %v", err)
	}
	defer s.Close()

	// Load state.
	var state = state.Load()

	// Initialize commands.
	commands.Init(s, state)
	defer commands.DeInit(s, state)

	// Wait for os.Interrupt.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, os.Kill)
	log.Println("Press Ctrl+C to exit.")
	<-stop
	log.Println("Gracefully shutting down.")
}
