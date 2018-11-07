package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/bot/utils"
)

var cmd = &sugo.Command{
	Trigger:      "publicroles",
	Description:  "Allows to manipulate public roles.",
	RequireGuild: true,
	HasParams:    true,
	Execute: func(req *sugo.Request) (err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 && len(req.Query) > 0 {
			_, err = req.NewResponse(sugo.ResponseWarning, "", "I need at least 3 symbols of the role name to look for one").Send()
			return
		}

		// Get guild.
		var guild *discordgo.Guild
		if guild, err = req.GetGuild(); err != nil {
			return
		}

		//Try to find roles based on query.
		var (
			roles discordgo.Roles
		)
		if roles, _, err = publicRoles.filter(req, guild.Roles, req.Query); err != nil {
			return
		}

		if len(roles) == 0 {
			_, err = req.NewResponse(sugo.ResponseWarning, "", "no public roles found with such name").Send()
			return
		}

		// Output roles we have found to the user.
		response := utils.FmtStringsSlice(utils.RolesToMentions(roles), ", ", "", 1500, " and more...", "")
		if _, err = req.NewResponse(sugo.ResponseInfo, "", response).Send(); err != nil {
			return
		}

		return
	},
	SubCommands: []*sugo.Command{
		myCmd,
		whoCmd,
		createCmd,
		registerCmd,
		unregisterCmd,
		joinCmd,
		leaveCmd,
		statsCmd,
	},
}
