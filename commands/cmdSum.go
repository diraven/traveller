package commands

import (
	"fmt"
	"log"
	"net/http"

	"github.com/PuerkitoBio/goquery"
	"github.com/bwmarrin/discordgo"
)

var cmdSum = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "sum",
		Description: "Пошук слова в словнику української мови",
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

		// Perform http request.
		resp, err := http.Get(fmt.Sprintf("http://sum.in.ua/?swrd=%s", optionMap["word"].StringValue()))
		if err != nil {
			log.Printf("%v", err)
			return
		}
		defer resp.Body.Close()
		if resp.StatusCode != 200 {
			log.Fatalf("status code error: %d %s", resp.StatusCode, resp.Status)
		}

		// Load the HTML document
		doc, err := goquery.NewDocumentFromReader(resp.Body)
		if err != nil {
			log.Fatal(err)
		}

		// Prepare embed.
		embed := &discordgo.MessageEmbed{
			Title:  optionMap["word"].StringValue(),
			URL:    fmt.Sprintf("http://sum.in.ua/?swrd=%s", optionMap["word"].StringValue()),
			Author: &discordgo.MessageEmbedAuthor{Name: "sum.in.ua", URL: "http://sum.in.ua/"},
		}
		if len(embed.Title) > 253 {
			embed.Title = embed.Title[:253] + "..."
		}

		// Find all the articles.
		articles := doc.Find("div[itemtype='http://schema.org/ScholarlyArticle']")

		// No articles found.
		if articles.Length() == 0 {
			embed.Description = fmt.Sprintf("Слово не знайдено. Що в біса таке %s?", embed.Title)
		}

		// One article found.
		if articles.Length() > 0 {
			s := articles.First()
			embed.Description = s.Find("div[itemprop='articleBody']").Text()
			log.Printf("%v", embed.Description)
			if len(embed.Description) > 2048 {
				embed.Description = embed.Description[:2048] + "..."
			}

			embed.Footer = &discordgo.MessageEmbedFooter{Text: s.Find("p.tom").Text()}
			if len(embed.Footer.Text) > 1024 {
				embed.Footer.Text = embed.Footer.Text[:1024] + "..."
			}
		}

		// Multiple articles found.
		if articles.Length() > 1 {
			embed.Description = embed.Description + fmt.Sprintf("\n\n Слово має [більше одного значення](%s).", embed.URL)
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
