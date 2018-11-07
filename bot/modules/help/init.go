package help

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"strings"
)

// Init initializes module on the given bot.
func Init(sg *sugo.Instance) (err error) {
	return sg.AddCommand(cmd)
}

// GetHint returns string that would be used to get current command's help.
func GetHint(req *sugo.Request) string {
	return fmt.Sprintf("`help %s`", req.Command.GetPath())
}

func generateHelpEmbed(req *sugo.Request, c *sugo.Command) (embed *discordgo.MessageEmbed, err error) {
	embed = &discordgo.MessageEmbed{
		Title:       c.GetPath(),
		Description: c.Description,
		Color:       sugo.ColorInfo,
	}
	// Get subcommands triggers respecting user permissions.
	var subcommandsTriggers = c.GetSubcommandsTriggers(req.Sugo, req)

	if len(c.SubCommands) > 0 {
		embed.Fields = append(embed.Fields,
			&discordgo.MessageEmbedField{
				Name:  "Subcommands:",
				Value: strings.Join(subcommandsTriggers, ", "),
			}, &discordgo.MessageEmbedField{
				Name:  "To get help on 'subcommand' type:",
				Value: fmt.Sprintf("help %s subcommand", c.GetPath()),
			})
	}
	return embed, nil

}

var cmd = &sugo.Command{
	Trigger:     "help",
	Description: "Shows help section for the appropriate command.",
	HasParams:   true,
	Execute: func(req *sugo.Request) (err error) {
		// Remove help command from the string
		req.Query = strings.TrimSpace(strings.TrimPrefix(req.Query, req.Command.Trigger))

		// Initialize embed.
		var embed *discordgo.MessageEmbed

		// Check if query is provided.
		if req.Query == "" {
			// No arguments, just the help itself.
			embed = &discordgo.MessageEmbed{
				Title:       "Available commands",
				Description: strings.Join(req.Sugo.RootCommand.GetSubcommandsTriggers(req.Sugo, req), ", "),
				Color:       sugo.ColorInfo,
				Fields: []*discordgo.MessageEmbedField{
					{
						Name:  "To get more info on 'something' try:",
						Value: "help something",
					},
				},
			}
		} else {
			// Arguments provided - search for respective applicable command.
			var command *sugo.Command
			if command, err = req.Sugo.FindCommand(req, req.Query); err != nil {
				return
			}

			// If command found.
			if command != nil {
				// Generate help embed.
				if embed, err = generateHelpEmbed(req, command); err != nil {
					return
				}
			}
		}

		// Now if embed is available, post it.
		if embed != nil {
			if _, err = req.Sugo.Session.ChannelMessageSendEmbed(req.Channel.ID, embed); err != nil {
				return
			}
			return
		}

		// Otherwise no embed is generated, this means command not found.
		if _, err = req.NewResponse(sugo.ResponseWarning, "", "command not found").Send(); err != nil {
			return
		}

		return
	},
}
