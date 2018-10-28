package settings

import (
	"github.com/pkg/errors"
	"github.com/spf13/viper"
)

// Settings is a settings storage object.
type Settings struct{}

// New initializes Settings storage and returns Settings object.
func New() (*Settings, error) {
	viper.SetConfigName("settings") // name of config file (without extension)

	viper.AddConfigPath("../..")
	viper.AddConfigPath("..")
	viper.AddConfigPath(".")
	viper.AddConfigPath("~")

	err := viper.ReadInConfig() // Find and read the config file
	if err != nil {
		return nil, errors.Wrap(err, "config file reading error")
	}

	return &Settings{}, nil
}

// Get returns setting value.
func (s *Settings) Get(name string) interface{} {
	return viper.Get(name)
}
