local WEBHOOK_URL = "https://discord.com/api/webhooks/834458016861782066/XBxrpvxJfXUf8jHGrFTk9njqcZtV9FIBm_KUyZRKn_pclrbLHAfXsyU6yjxuIOJV0nCt"

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local function fireWebhook(content)
	HttpService:PostAsync(WEBHOOK_URL, HttpService:JSONEncode({content = content}))
end

Players.PlayerAdded:Connect(function(player)
	fireWebhook("status=player_joined/player_id=" .. tostring(player.UserId) .. "/place_id=" .. tostring(game.PlaceId))
end)

Players.PlayerRemoving:Connect(function(player)
	fireWebhook("status=player_left/player_id=" .. tostring(player.UserId) .. "/place_id=" .. tostring(game.PlaceId))
end)