package commands

import (
	"fmt"
	"math/rand"

	"github.com/bwmarrin/discordgo"
)

var templates = []string{
	"%s прикладає %s по спині величезним сомом.",
	"%s демонструє %s щорічну заяву Арестовича на звільнення.",
	"%s щось кричить %s на вухо.",
	"%s уважно дивиться %s в очі.",
	"%s хизується електрохарчуванням перед %s.",
	"%s шепоче %s на вухо \"русні пизда\".",
	"%s шепоче %s на вухо що стало краще.",
	"%s шепоче %s на вухо що стало гірше.",
	"%s показує %s пальцем на напис \"зрада\".",
	"%s показує %s пальцем на напис \"перемога\".",
	"%s показує %s пальцем на напис \"переможна зрада\".",
	"%s показує %s пальцем на напис \"зраджена перемога\".",
	"%s показує %s пальцем на напис \"зрадоперемога\".",
	"%s підозріло зиркає на %s.",
	"%s тихенько ліпить слоупока %s на спину.",
	"%s бідкається, %s розводить руками.",
	"%s каже %s \"Це ж було вже!\".",
	"%s вмовляє %s проголосувати за Ляшка.",
	"%s демонструє свої музичні здібності. %s плаче.",
	"%s демонструє свої вокальні здібності. %s плаче.",
	"%s демонструє супер сайян. %s каже \"ок\".",
	"%s конем б'є короля у %s. Це гол.",
	"%s п'є чай з молоком. %s каже, що це мєрзость.",
	"%s робить %s комплімент. Це надзвичайно ефективно!",
	"%s обіймає %s. Всі інші заздрять.",
	"%s нагадує %s що пора на завод.",
	"%s пропонує %s виміряти довжину мосту.",
	"%s пропонує %s розкрутитися.",
	"%s slaps %s around with small 50Lbs Linux manual.",
	"%s пропонує %s зупинитися і послухати.",
	"%s просить %s покликати його мішок з м'ясом.",
}

var cmdSlap = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "slap",
		Description: "???",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionUser,
				Name:        "user",
				Description: "Користувач",
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

		// Respond.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{
					{
						Description: fmt.Sprintf(templates[rand.Intn(len(templates))], i.Member.Mention(), (optionMap["user"]).UserValue(s).Mention()),
					},
				},
			},
		})
	},
}
