package publicroles

import (
	"database/sql"
	"github.com/diraven/sugo"
)

// Package-level database object.
var db *sql.DB

// Init initializes module on the given bot.
func Init(sg *sugo.Instance, database *sql.DB) (err error) {
	db = database

	return sg.AddCommand(cmd)
}
