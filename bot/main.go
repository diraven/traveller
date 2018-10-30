package main

import (
	"database/sql"
	"fmt"
	"github.com/diraven/sugo"
	"github.com/diraven/sugo/examples/info"
	"github.com/diraven/sugo/examples/test"
	_ "github.com/lib/pq"
	"github.com/sirupsen/logrus"
	"gitlab.com/diraven/crabot/bot/modules/help"
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
	if err := test.Init(bot); err != nil {
		log.Println(err)
		return
	}
	if err := help.Init(bot); err != nil {
		log.Println(err)
		return
	}
	if err := info.Init(bot); err != nil {
		log.Println(err)
		return
	}
	//if err := mod.Init(bot); err != nil {
	//	log.Println(err)
	//	return
	//}
	//if err := publicroles.Init(bot, db); err != nil {
	//	log.Println(err)
	//	return
	//}

	// Start the bot.
	if err := bot.Startup(os.Getenv("DISCORD_BOT_TOKEN")); err != nil {
		bot.HandleError(err)
	}
}
