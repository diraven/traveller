package publicroles

import (
	"fmt"
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/sugo"
	"github.com/pkg/errors"
	"github.com/texttheater/golang-levenshtein/levenshtein"
	"github.com/volatiletech/sqlboiler/queries/qm"
	"gitlab.com/diraven/crabot/bot/models"
	"strings"
)

func find(req *sugo.Request, q string) (roles discordgo.Roles, err error) {
	// Remove unnecessary spaces.
	q = strings.TrimSpace(q)

	// Make sure at least 3 symbols are provided.
	if len(q) < 3 {
		return nil, errors.New("query must contain at least 3 symbols")
	}

	// Get the list of roles from the DB for the given guild.
	var dbPublicRoles models.PublicrolesPublicroleSlice
	if dbPublicRoles, err = models.PublicrolesPublicroles(
		qm.From("publicroles_publicrole pr"),
		qm.InnerJoin("mydiscord_guilds g on g.id = pr.guild_id"),
		qm.Where("g.discord_id = ?", req.Channel.GuildID),
	).All(req.Ctx, db); err != nil {
		return
	}

	// Get the list of roles from discord. We can rely on doing this since top level command requires guild.
	discordPublicRoles, err := req.Sugo.Session.GuildRoles(req.Channel.GuildID)

	// Now for each stored public role from our DB:
outer:
	for _, dbRole := range dbPublicRoles {
		// For each current guild discord role:
		for _, discordRole := range discordPublicRoles {
			// If we have found the role that is both stored in DB and in discord - it's a public role.
			if dbRole.DiscordID == discordRole.ID {
				// Add newly found role to the list.
				discordPublicRoles = append(discordPublicRoles, discordRole)

				// Continue with the next role.
				continue outer
			}
		}

		// If no respective discord role found, delete it from our db.
		if _, err = dbRole.Delete(req.Ctx, db); err != nil {
			return
		}
	}

	// Now we have got a clean list of discordPublicRoles each of which does really exist and is public.
	// Now try to find exact match.
	for _, role := range discordPublicRoles {
		if role.ID == q || // If numeric role ID matches.
			fmt.Sprintf("<@&%s>", role.ID) == q || // If it's role mention.
			strings.ToLower(role.Name) == strings.ToLower(q) { // If role name matches.
			roles = append(roles, role)
		}
	}

	// Return results if we found any.
	if len(roles) > 0 {
		return
	}

	// If no exact matches to be found, try fuzzy match.
	var d int
	var expectedEditDistance = 2
	for _, role := range discordPublicRoles {
		d = levenshtein.DistanceForStrings(
			[]rune(strings.ToLower(role.Name)),
			[]rune(strings.ToLower(q)),
			levenshtein.DefaultOptions,
		)
		// If edit distance is less then equal then expected:
		if d <= expectedEditDistance {
			// Add the role id to the suggested list.
			roles = append(roles, role)
			break
		}
	}

	// Return our results, if any.
	if len(roles) > 0 {
		return
	}

	// Found no roles.
	return
}
