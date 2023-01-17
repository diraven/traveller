package commands

import (
	"encoding/json"
	"log"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var cmdTest = &Command{

	Init: func(s *discordgo.Session, state *state.State) error {
		// Register command.
		definition := &discordgo.ApplicationCommand{
			Name:        "test",
			Description: "test command",
		}
		for GuildID := range state.Guilds {
			_, err := s.ApplicationCommandCreate(s.State.User.ID, GuildID, definition)
			if err != nil {
				log.Panicf("Cannot create '%v' command: %v", definition.Name, err)
			}
		}

		min_values := 1

		// Add handler.
		s.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
			switch i.Type {
			// Command itself.
			case discordgo.InteractionApplicationCommand:
				if i.ApplicationCommandData().Name == definition.Name {
					response := &discordgo.InteractionResponse{
						Type: discordgo.InteractionResponseModal,
						Data: &discordgo.InteractionResponseData{
							CustomID: "modal_faq_" + i.Interaction.Member.User.ID,
							Title:    "ЧаПи",
							Components: []discordgo.MessageComponent{
								discordgo.ActionsRow{
									Components: []discordgo.MessageComponent{
										// discordgo.TextInput{
										// 	CustomID:    "opinion",
										// 	Label:       "What is your opinion on them?",
										// 	Style:       discordgo.TextInputShort,
										// 	Placeholder: "Don't be shy, share your opinion with us",
										// 	Required:    true,
										// 	MaxLength:   300,
										// 	MinLength:   10,
										// },
										discordgo.SelectMenu{
											MenuType:    discordgo.StringSelectMenu,
											CustomID:    "entry",
											Placeholder: "Оберіть питання.",
											MaxValues:   1,
											MinValues:   &min_values,
											Options: []discordgo.SelectMenuOption{
												{Label: "test1", Value: "test1", Description: "test description 1"},
												{Label: "test2", Value: "test2", Description: "test description 2"},
											},
										},
									},
								},
							},
						},
					}
					resp, _ := json.Marshal(response)
					log.Printf("%s", string(resp))
					err := s.InteractionRespond(i.Interaction, response)
					if err != nil {
						panic(err)
					}

				}

			// Processing modal response.
			case discordgo.InteractionModalSubmit:
				err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
					Type: discordgo.InteractionResponseChannelMessageWithSource,
					Data: &discordgo.InteractionResponseData{
						Content: "Thank you for taking your time to fill this survey",
						Flags:   discordgo.MessageFlagsEphemeral,
					},
				})
				if err != nil {
					panic(err)
				}
				data := i.ModalSubmitData()

				if !strings.HasPrefix(data.CustomID, "modals_survey") {
					return
				}

				userid := strings.Split(data.CustomID, "_")[2]
				log.Printf("%s", userid)
				// _, err = s.ChannelMessageSend(*ResultsChannel, fmt.Sprintf(
				// 	"Feedback received. From <@%s>\n\n**Opinion**:\n%s\n\n**Suggestions**:\n%s",
				// 	userid,
				// 	data.Components[0].(*discordgo.ActionsRow).Components[0].(*discordgo.TextInput).Value,
				// 	data.Components[1].(*discordgo.ActionsRow).Components[0].(*discordgo.TextInput).Value,
				// ))
				if err != nil {
					panic(err)
				}
			}

		})

		return nil
	},
}
