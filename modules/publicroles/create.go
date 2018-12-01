package publicroles

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"github.com/pkg/errors"
	"gitlab.com/diraven/crabot/modules/help"
	"strings"
)

var createCmd = &sugo.Command{
	Trigger:             "create",
	Description:         "Creates new guild role with the given name and makes it public.",
	PermissionsRequired: discordgo.PermissionManageRoles,
	HasParams:           true,
	Execute: func(req *sugo.Request) (resp *sugo.Response, err error) {
		// Make sure at least 3 symbols are provided in the query.
		if len(req.Query) < 3 {
			resp = req.NewResponse(sugo.ResponseWarning, "", "role name must have at least 3 symbols")
			return
		}

		// Get guild.
		var guild *discordgo.Guild
		if guild, err = req.GetGuild(); err != nil {
			return
		}

		// Variable to hold roles lists.
		var roles discordgo.Roles

		// Try to filter the role in our db public roles list first.
		var fuzzy bool
		if roles, fuzzy, err = publicRoles.filter(req, guild.Roles, req.Query); err != nil {
			return
		}
		if len(roles) > 0 && !fuzzy {
			// Role with such name already exists.
			resp = req.NewResponse(sugo.ResponseWarning, "", "this role is already public")
			return
		}

		// Now try to filter role in the guild roles list, get all guild roles.
		if roles, err = req.Sugo.Session.GuildRoles(guild.ID); err != nil {
			return
		}
		for _, role := range roles {
			if strings.ToLower(role.Name) == strings.ToLower(req.Query) {
				// We have found the role with the same name.
				resp = req.NewResponse(sugo.ResponseWarning, "", "role with such name already exists, try to register it as public instead of creating new, see "+help.GetHint(req)+" for details ")
				return
			}
		}

		// If we did not filter any match, try to create new role via Discord API.
		var role *discordgo.Role
		if role, err = req.Sugo.Session.GuildRoleCreate(guild.ID); err != nil {
			return nil, errors.Wrap(err, "unable to create new discord guild role")
		}

		// Set new role properties.
		if role, err = req.Sugo.Session.GuildRoleEdit(guild.ID, role.ID, req.Query, 0, false, 0, true); err != nil {
			return
		}

		// And registerRole new role to the list of the public roles in the DB.
		if err = publicRoles.register(req, role); err != nil {
			return
		}

		// And notify user about success.
		if err = req.AddReaction(sugo.ReactionOk); err != nil {
			return
		}

		return
	},
}
