package aliases

import (
	"database/sql"
	"github.com/diraven/sugo"
	"github.com/volatiletech/sqlboiler/queries/qm"
	"gitlab.com/diraven/crabot/models"
	"strings"
)

func makeMiddleware(db *sql.DB) sugo.RequestMiddleware {
	return func(req *sugo.Request) (err error) {
		// Make sure request is from guild chat.
		if req.Channel.GuildID == "" {
			return
		}

		var aliases models.MydiscordAliasSlice

		if aliases, err = models.MydiscordAliases(
			qm.InnerJoin("mydiscord_guild g ON g.id = mydiscord_alias.guild_id"),
			qm.Where("g.discord_id = ?", req.Channel.GuildID),
		).All(req.Ctx, db); err != nil {
			return
		}

		// Now search query string for each alias and apply the one that matches if any.
		for _, alias := range aliases {
			if strings.HasPrefix(req.Query, alias.Source) {
				req.Query = strings.Replace(req.Query, alias.Source, alias.Target, 1)
				return
			}
		}

		// No aliases applied.
		return
	}
}

// Init initializes module on the given bot.
func Init(sg *sugo.Instance, db *sql.DB) {
	// Add alias processing middleware.
	sg.AddRequestMiddleware(makeMiddleware(db))
}
