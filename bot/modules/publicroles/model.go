package publicroles

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"github.com/texttheater/golang-levenshtein/levenshtein"
	"github.com/volatiletech/sqlboiler/boil"
	"github.com/volatiletech/sqlboiler/queries/qm"
	"gitlab.com/diraven/crabot/bot/models"
	"strings"
)

type rolesStorage struct{}

var publicRoles = &rolesStorage{}

func (s *rolesStorage) register(req *sugo.Request, role *discordgo.Role) (err error) {
	// Get dbGuild (it should have been already created when the request was built).
	var dbGuild *models.MydiscordGuild
	if dbGuild, err = models.MydiscordGuilds(
		qm.Where("discord_id = ?", req.Channel.GuildID),
	).One(req.Ctx, db); err != nil {
		return
	}

	// Try to create new role and add it into the database.
	var dbRole *models.PublicrolesPublicrole
	dbRole = &models.PublicrolesPublicrole{
		DiscordID: role.ID,
		GuildID:   dbGuild.ID,
	}

	if err = dbRole.Insert(req.Ctx, db, boil.Infer()); err != nil {
		return
	}

	return
}

func (s *rolesStorage) unregister(req *sugo.Request, role *discordgo.Role) (err error) {
	// Delete role from the DB.
	var dbRole *models.PublicrolesPublicrole
	if dbRole, err = models.PublicrolesPublicroles(
		qm.Where("discord_id = ?", role.ID),
	).One(req.Ctx, db); err != nil {
		return
	}

	// Delete it.
	dbRole.Delete(req.Ctx, db)

	return
}

func (s *rolesStorage) sync(
	req *sugo.Request,
	roles discordgo.Roles,
) (
	publicRoles discordgo.Roles,
	err error,
) {
	// Get the list of public roles from the DB for the given guild.
	var dbPublicRoles models.PublicrolesPublicroleSlice
	if dbPublicRoles, err = models.PublicrolesPublicroles(
		qm.InnerJoin("mydiscord_guild g ON g.id = publicroles_publicrole.guild_id"),
		qm.Where("g.discord_id = ?", req.Channel.GuildID),
	).All(req.Ctx, db); err != nil {
		return
	}

	// Get guild.
	var guild *discordgo.Guild
	if guild, err = req.GetGuild(); err != nil {
		return
	}

	// Now for each stored public role from our DB:
outer:
	for _, dbRole := range dbPublicRoles {
		// For each current guild discord role:
		for _, discordRole := range guild.Roles {
			// If we have found the role that is both stored in DB and in discord - it's a public role.
			if dbRole.DiscordID == discordRole.ID {

				// For each provided role:
				for _, providedRole := range roles {
					// If this is one of the roles we are looking for:
					if providedRole.ID == dbRole.DiscordID {
						// Add newly found role to the list.
						publicRoles = append(publicRoles, discordRole)
					}
				}

				// Continue with the next role.
				continue outer
			}
		}

		// If no respective discord role found, delete it from our db.
		if _, err = dbRole.Delete(req.Ctx, db); err != nil {
			return
		}
	}

	// Return synced and cleaned up public roles list.
	return
}

func (s *rolesStorage) filter(
	req *sugo.Request,
	unfilteredRoles discordgo.Roles,
	q string,
) (
	filteredRoles discordgo.Roles,
	fuzzy bool,
	err error,
) {
	// Remove unnecessary spaces.
	q = strings.TrimSpace(q)

	// Now for each stored public role from our DB:
	var publicRoles []*discordgo.Role
	if publicRoles, err = s.sync(req, unfilteredRoles); err != nil {
		return
	}
	// If query is empty - we just return our filtered list of roles:
	if q == "" {
		filteredRoles = publicRoles
		return
	}

	// Now we have got a clean list of publicRoles each of which does really exist and is indeed public.
	// Now try to filter exact match.
	for _, role := range publicRoles {
		if role.ID == q || // If numeric role ID matches.
			fmt.Sprintf("<@&%s>", role.ID) == q || // If it's role mention.
			strings.ToLower(role.Name) == strings.ToLower(q) { // If role name matches exactly.
			filteredRoles = append(filteredRoles, role)
			return // exact match found
		}
	}

	// If no exact matches to be found, try fuzzy match.
	var d int
	var expectedEditDistance = 2
	for _, role := range publicRoles {
		d = levenshtein.DistanceForStrings(
			[]rune(strings.ToLower(role.Name)),
			[]rune(strings.ToLower(q)),
			levenshtein.DefaultOptions,
		)
		// If role name contains name or distance is less or equal then expected:
		if strings.Contains(strings.ToLower(role.Name), strings.ToLower(q)) || d <= expectedEditDistance {
			// Add the role id to the suggested list.
			filteredRoles = append(filteredRoles, role)
		}
	}

	// Return our results, if any.
	if len(filteredRoles) > 0 {
		fuzzy = true
		return
	}

	// Found no filteredRoles.
	return
}
