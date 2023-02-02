package commands

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"github.com/bwmarrin/discordgo"
)

type sum20Response struct {
	Entry string `json:"entry"`
}

var cmdSum20 = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "sum20",
		Description: "Пошук слова в сучаснішому словнику української мови",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionString,
				Name:        "word",
				Description: "слово",
				Required:    true,
			},
		},
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		// Convert options to map.
		options := i.ApplicationCommandData().Options
		optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
		for _, opt := range options {
			optionMap[opt.Name] = opt
		}

		resp, err := http.Get(fmt.Sprintf("https://sum20ua.com/api/DictEntry/searchEntry/%s", optionMap["word"].StringValue()))
		if err != nil {
			log.Printf("%v", err)
			return
		}
		defer resp.Body.Close()
		if resp.StatusCode != 200 {
			log.Fatalf("status code error: %d %s", resp.StatusCode, resp.Status)
		}

		// Load JSON.
		response := &sum20Response{}
		data, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Printf("%v", err)
		}
		err = json.Unmarshal(data, response)
		if err != nil {
			log.Printf("%v", err)
		}

		// Load HTML.
		doc, err := goquery.NewDocumentFromReader(strings.NewReader(response.Entry))
		if err != nil {
			log.Fatal(err)
		}

		// Prepare embed.
		embed := &discordgo.MessageEmbed{
			Title:  optionMap["word"].StringValue(),
			URL:    "https://sum20ua.com/",
			Author: &discordgo.MessageEmbedAuthor{Name: "sum20.in.ua", URL: "https://sum20ua.com/"},
			Footer: &discordgo.MessageEmbedFooter{Text: "СЛОВНИК УКРАЇНСЬКОЇ МОВИ ONLINE. ТОМИ 1-12."},
		}
		if len(embed.Title) > 253 {
			embed.Title = embed.Title[:253] + "..."
		}

		if doc.Find(".WORD").Text() != "ПІДКУ́РЮВАЧ" {
			// Word found.
			embed.Description = doc.Text()
			if len(embed.Description) > 2048 {
				embed.Description = embed.Description[:2048] + "..."
			}
		} else {
			// Word not found.
			embed.Description = fmt.Sprintf("Слово не знайдено. Що в біса таке %s?", embed.Title)
		}

		// Respond.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
			},
		})
	},
}
