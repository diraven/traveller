package main

import (
	"database/sql"
	"fmt"
	"github.com/diraven/sugo"
	_ "github.com/lib/pq"
	"github.com/sirupsen/logrus"
	"gitlab.com/diraven/crabot/bot/modules/aliases"
	"gitlab.com/diraven/crabot/bot/modules/help"
	"gitlab.com/diraven/crabot/bot/modules/info"
	"gitlab.com/diraven/crabot/bot/modules/mod"
	"gitlab.com/diraven/crabot/bot/modules/publicroles"
	"gitlab.com/diraven/crabot/bot/modules/test"
	"gitlab.com/diraven/crabot/bot/settings"
	"log"
	"os"
)

func main() {
	// Get config.
	cfg, err := settings.New()
	if err != nil {
		log.Fatal("config file reading error: " + err.Error())
	}

	// Initialize DB connection.
	db, err := sql.Open(
		"postgres",
		fmt.Sprintf(
			"dbname=%s user=%s password=%s sslmode=disable",
			cfg.Get("DATABASES.default.NAME"),
			cfg.Get("DATABASES.default.USER"),
			cfg.Get("DATABASES.default.PASSWORD"),
		),
	)
	defer db.Close()
	if err != nil {
		logrus.Fatal("unable to set up DB connection: ", err)
	}

	// Create new bot instance.
	bot := sugo.New()

	// Set bot's default trigger.
	bot.DefaultTrigger = "."

	// Set custom isTriggered function.
	bot.IsTriggered = isTriggeredFactory(db)

	// Initialize modules.
	aliases.Init(bot, db)
	test.Init(bot)
	help.Init(bot)
	info.Init(bot)
	mod.Init(bot)
	publicroles.Init(bot, db)

	// Start the bot.
	if err := bot.Startup(os.Getenv("DISCORD_BOT_TOKEN")); err != nil {
		bot.HandleError(nil, err)
	}
}
