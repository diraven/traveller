package commands

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var cmdTraveller = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "t",
		Description: "Подорожній",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionSubCommand,
				Name:        "farm",
				Description: "Вирощувати їжу",
			},
			{
				Type:        discordgo.ApplicationCommandOptionSubCommand,
				Name:        "defend",
				Description: "Захищатися від нападу",
			},
			{
				Type:        discordgo.ApplicationCommandOptionSubCommand,
				Name:        "repair",
				Description: "Ремонтувати будівлі",
			},
		},
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		var embed *discordgo.MessageEmbed

		switch i.ApplicationCommandData().Options[0].Name {
		case "farm", "defend", "repair":
			userState := state.State.GetUser(i.Member.User)
			userState.T.Action = i.ApplicationCommandData().Options[0].Name
			state.State.Save()
			embed = &discordgo.MessageEmbed{
				Title:       "Ви обрали дію на наступний раунд:",
				Description: i.ApplicationCommandData().Options[0].Name,
			}

		}

		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{embed},
			},
		})
	},
}
