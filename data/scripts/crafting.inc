Common_EventScript_CraftingStation::
	lock
	faceplayer
	msgbox Crafting_Text_Intro, MSGBOX_DEFAULT
	msgbox Crafting_Text_BuyMaterials, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, Crafting_EventScript_BuyMaterials

Crafting_EventScript_CategoryMenu::
	special Crafting_ChooseCategory
	special Crafting_DecodeSelection
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, Crafting_EventScript_Exit
	goto_if_eq VAR_RESULT, CRAFTING_CATEGORY_EXIT, Crafting_EventScript_Exit
	copyvar VAR_0x8004, VAR_RESULT
	special Crafting_ChooseOutput
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, Crafting_EventScript_CategoryMenu
	special Crafting_DecodeSelection
	goto_if_eq VAR_RESULT, CRAFTING_MENU_NO_ITEMS, Crafting_EventScript_NoItems
	copyvar VAR_0x8007, VAR_RESULT
	special Crafting_PrepareRecipe
	goto_if_eq VAR_RESULT, FALSE, Crafting_EventScript_InvalidOutput
	special Crafting_CheckRecipe
	goto_if_eq VAR_RESULT, FALSE, Crafting_EventScript_MissingMaterials
	msgbox Crafting_Text_Recipe, MSGBOX_DEFAULT
	msgbox Crafting_Text_ConfirmCraft, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, Crafting_EventScript_ConfirmCraft
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_BuyMaterials::
	pokemart Crafting_Pokemart_Materials
	msgbox Crafting_Text_MaterialsThanks, MSGBOX_DEFAULT
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_ConfirmCraft::
	special Crafting_CreateItem
	goto_if_eq VAR_RESULT, 0, Crafting_EventScript_Success
	goto_if_eq VAR_RESULT, 1, Crafting_EventScript_MissingMaterials
	goto_if_eq VAR_RESULT, 2, Crafting_EventScript_BagFull
	goto Crafting_EventScript_InvalidOutput

Crafting_EventScript_MissingMaterials::
	msgbox Crafting_Text_Recipe, MSGBOX_DEFAULT
	msgbox Crafting_Text_MissingMaterials, MSGBOX_DEFAULT
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_Success::
	msgbox Crafting_Text_Success, MSGBOX_DEFAULT
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_BagFull::
	msgbox Crafting_Text_BagFull, MSGBOX_DEFAULT
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_NoItems::
	msgbox Crafting_Text_NoItems, MSGBOX_DEFAULT
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_InvalidOutput::
	msgbox Crafting_Text_InvalidOutput, MSGBOX_DEFAULT
	goto Crafting_EventScript_CategoryMenu

Crafting_EventScript_Exit::
	release
	end

Crafting_Text_Intro:
	.string "I'm the CENTER'S item fabricator.\p"
	.string "Choose an item and I'll show you\n"
	.string "the materials needed to make it.$"

	.align 2
Crafting_Pokemart_Materials:
	.2byte ITEM_ORAN_BERRY
	.2byte ITEM_CHERI_BERRY
	.2byte ITEM_RED_SHARD
	.2byte ITEM_BLUE_SHARD
	.2byte ITEM_GREEN_SHARD
	.2byte ITEM_YELLOW_SHARD
	pokemartlistend

Crafting_Text_BuyMaterials:
	.string "Need supplies? You can buy crafting\n"
	.string "materials here. Want to shop?$"

Crafting_Text_MaterialsThanks:
	.string "Good luck with your crafting!$"

Crafting_Text_Recipe:
	.string "Recipe for {STR_VAR_1}:\n"
	.string "{STR_VAR_2} + {STR_VAR_3}$"

Crafting_Text_ConfirmCraft:
	.string "Craft this item?$"

Crafting_Text_MissingMaterials:
	.string "You don't have all the required\n"
	.string "materials in your BAG.$"

Crafting_Text_Success:
	.string "Created {STR_VAR_1}!$"

Crafting_Text_BagFull:
	.string "Your BAG has no room for that item.$"

Crafting_Text_NoItems:
	.string "There are no craftable items in\n"
	.string "this category.$"

Crafting_Text_InvalidOutput:
	.string "This item can't be crafted here.$"
