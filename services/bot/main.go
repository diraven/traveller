package main

import (
	"database/sql"
	"fmt"
	"github.com/diraven/sugo"
	_ "github.com/lib/pq"
	"github.com/sirupsen/logrus"
	"gitlab.com/diraven/crabot/modules/aliases"
	"gitlab.com/diraven/crabot/modules/destiny2"
	"gitlab.com/diraven/crabot/modules/goharu"
	"gitlab.com/diraven/crabot/modules/help"
	"gitlab.com/diraven/crabot/modules/info"
	"gitlab.com/diraven/crabot/modules/mod"
	"gitlab.com/diraven/crabot/modules/publicroles"
	"gitlab.com/diraven/crabot/modules/test"
	"gitlab.com/diraven/crabot/settings"
	"log"
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

	log.Println("starting bot...")

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
	destiny2.Init(bot)
	goharu.Init(bot)

	// Start the bot.
	if err := bot.Startup(fmt.Sprintf("%s", cfg.Get("token"))); err != nil {
		bot.HandleError(nil, err)
	}

	// Notify about successful shutdown.
	log.Println("bot was shut down")
}
