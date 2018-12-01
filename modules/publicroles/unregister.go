package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"gitlab.com/diraven/crabot/utils"
)

var unregisterCmd = &sugo.Command{
	Trigger:             "unregister",
	Description:         "Makes given role not public (does not delete the role itself).",
	PermissionsRequired: discordgo.PermissionManageRoles,
	HasParams:           true,
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 {
			resp = req.NewResponse(sugo.ResponseWarning, "", "I need at least 3 symbols of the role name to look for one")
			return
		}

		// Get guild.
		var guild *discordgo.Guild
		if guild, err = req.GetGuild(); err != nil {
			return
		}

		// Try to find role based on query.
		var roles discordgo.Roles
		var fuzzy bool
		if roles, fuzzy, err = publicRoles.filter(req, guild.Roles, req.Query); err != nil {
			return
		}

		// If exact match found:
		if len(roles) == 1 && !fuzzy {

			// Delete role.
			if err = publicRoles.unregister(req, roles[0]); err != nil {
				return
			}

			// Notify user.
			resp = req.NewResponse(sugo.ResponseSuccess, "", "role "+utils.RoleToMention(roles[0])+" not publuc any more")
			return
		}

		// TODO: add "try one of these instead" functionality
		resp = req.NewResponse(sugo.ResponseWarning, "", "no public roles with such name found")
		return
	},
}
