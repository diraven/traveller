use crate::{Context, Error};
use chrono;
use poise;
use reqwest;
use serde_json;

const API_ROOT_URL: &str = "https://russianwarship.rip/api/v2";

#[poise::command(slash_command)]
pub async fn rusni_pyzda(ctx: Context<'_>) -> Result<(), Error> {
    let now = chrono::Utc::now();
    let url = format!(
        "{}/statistics/{}",
        API_ROOT_URL,
        now.format("%Y-%m-%d").to_string()
    );
    let response: serde_json::Value = reqwest::get(url).await?.json().await?;

    let errors = response.get("errors").unwrap_or(&serde_json::Value::Null);
    if errors.is_null() {
        let data = response.get("data").unwrap();
        let mut embed = poise::serenity_prelude::CreateEmbed::default()
            .title(format!(
                "Втрати ворога станом на {}",
                data.get("date").unwrap().as_str().unwrap()
            ))
            .thumbnail(
                "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_the_Ukrainian_Armed_Forces.svg/1024px-Emblem_of_the_Ukrainian_Armed_Forces.svg.png"
            );

        for (key, value) in data.get("stats").unwrap().as_object().unwrap() {
            embed = embed.field(
                key,
                format!(
                    "{} (+{})",
                    value.as_u64().unwrap().to_string(),
                    data.get("increase")
                        .unwrap()
                        .as_object()
                        .unwrap()
                        .get(key)
                        .unwrap()
                        .as_u64()
                        .unwrap()
                        .to_string()
                ),
                true,
            );
        }

        ctx.send(poise::CreateReply::default().embed(embed)).await?;
        return Ok(());
    } else {
        let embed = poise::serenity_prelude::CreateEmbed::default()
            .title(format!(
                "Помилка отримання даних: {}",
                response.get("message").unwrap()
            ))
            .color((255, 0, 0))
            .description(format!("{}", errors));

        ctx.send(poise::CreateReply::default().embed(embed)).await?;
        return Ok(());
    }
}
