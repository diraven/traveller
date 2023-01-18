package commands

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/bwmarrin/discordgo"
)

type ruPi struct {
	Message string   `json:"message"`
	Data    ruPiData `json:"data"`
}

type ruPiData struct {
	Date     string    `json:"date"`
	Day      string    `json:"day"`
	Resource string    `json:"resource"`
	Stats    ruPiStats `json:"stats"`
	Increase ruPiStats `json:"increase"`
}

type ruPiStats struct {
	PersonnelUnits           int `json:"personnel_units"`
	Tanks                    int `json:"tanks"`
	ArmouredFightingVehicles int `json:"armoured_fighting_vehicles"`
	ArtillerySystems         int `json:"artillery_systems"`
	Mlrs                     int `json:"mlrs"`
	AaWarfareSystems         int `json:"aa_warfare_systems"`
	Planes                   int `json:"planes"`
	Helicopters              int `json:"helicopters"`
	VehiclesFuelYanks        int `json:"vehicles_fuel_tanks"`
	WarshipsCutters          int `json:"warships_cutters"`
	CruiseMissiles           int `json:"cruise_missiles"`
	UavSystems               int `json:"uav_systems"`
	SpecialMilitaryEquip     int `json:"special_military_equip"`
	AtgmSrbmSystems          int `json:"atgm_srbm_systems"`
}

var cmdRusniPizda = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "rusni-pizda",
		Description: "Русні - пизда!",
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		// Get and parse data.
		var myClient = &http.Client{Timeout: 10 * time.Second}
		r, err := myClient.Get("https://russianwarship.rip/api/v1/statistics/latest")
		if err != nil {
			log.Panicf(err.Error())
		}
		defer r.Body.Close()

		rupi := &ruPi{}
		json.NewDecoder(r.Body).Decode(rupi)

		// Respond.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{
					{
						Description: "[Втрати ворога](" + rupi.Data.Resource + ") станом на " + rupi.Data.Date,
						Fields: []*discordgo.MessageEmbedField{
							{Name: "Особовий склад", Value: strconv.Itoa(rupi.Data.Stats.PersonnelUnits) + " (+" + strconv.Itoa(rupi.Data.Increase.PersonnelUnits) + ")"},
							{Name: "Танки", Value: strconv.Itoa(rupi.Data.Stats.Tanks) + " (+" + strconv.Itoa(rupi.Data.Increase.Tanks) + ")"},
							{Name: "Бойові Броньовані Машини", Value: strconv.Itoa(rupi.Data.Stats.ArmouredFightingVehicles) + " (+" + strconv.Itoa(rupi.Data.Increase.ArmouredFightingVehicles) + ")"},
							{Name: "Ствольна артилерія", Value: strconv.Itoa(rupi.Data.Stats.ArtillerySystems) + " (+" + strconv.Itoa(rupi.Data.Increase.ArtillerySystems) + ")"},
							{Name: "Реактивна артилерія", Value: strconv.Itoa(rupi.Data.Stats.Mlrs) + " (+" + strconv.Itoa(rupi.Data.Increase.Mlrs) + ")"},
							{Name: "Засоби ППО", Value: strconv.Itoa(rupi.Data.Stats.AaWarfareSystems) + " (+" + strconv.Itoa(rupi.Data.Increase.AaWarfareSystems) + ")"},
							{Name: "Літаки", Value: strconv.Itoa(rupi.Data.Stats.Planes) + " (+" + strconv.Itoa(rupi.Data.Increase.Planes) + ")"},
							{Name: "Гелікоптери", Value: strconv.Itoa(rupi.Data.Stats.Helicopters) + " (+" + strconv.Itoa(rupi.Data.Increase.Helicopters) + ")"},
							{Name: "Логістика", Value: strconv.Itoa(rupi.Data.Stats.VehiclesFuelYanks) + " (+" + strconv.Itoa(rupi.Data.Increase.VehiclesFuelYanks) + ")"},
							{Name: "Кораблі та катери", Value: strconv.Itoa(rupi.Data.Stats.WarshipsCutters) + " (+" + strconv.Itoa(rupi.Data.Increase.WarshipsCutters) + ")"},
							{Name: "Крилаті ракети", Value: strconv.Itoa(rupi.Data.Stats.CruiseMissiles) + " (+" + strconv.Itoa(rupi.Data.Increase.CruiseMissiles) + ")"},
							{Name: "БПЛА", Value: strconv.Itoa(rupi.Data.Stats.UavSystems) + " (+" + strconv.Itoa(rupi.Data.Increase.UavSystems) + ")"},
							{Name: "Спец. техніка", Value: strconv.Itoa(rupi.Data.Stats.SpecialMilitaryEquip) + " (+" + strconv.Itoa(rupi.Data.Increase.SpecialMilitaryEquip) + ")"},
							{Name: "Протитанкові засоби, балістичні ракети", Value: strconv.Itoa(rupi.Data.Stats.AtgmSrbmSystems) + " (+" + strconv.Itoa(rupi.Data.Increase.AtgmSrbmSystems) + ")"},
						},
						URL:       rupi.Data.Resource,
						Thumbnail: &discordgo.MessageEmbedThumbnail{URL: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_the_Ukrainian_Armed_Forces.svg/1024px-Emblem_of_the_Ukrainian_Armed_Forces.svg.png"},
					},
				},
			},
		})
	},
}
