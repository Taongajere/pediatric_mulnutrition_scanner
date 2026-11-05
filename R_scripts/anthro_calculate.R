
library(anthro)
library(jsonlite)

# Read screening information sent by Python
input <- fromJSON(file("stdin"))

# Calculate WHO anthropometric indicators
result <- anthro_zscores(
    sex = input$sex,
    age = as.numeric(input$age_days),
    is_age_in_month = FALSE,
    weight = as.numeric(input$weight),
    lenhei = as.numeric(input$height),
    measure = input$measure,
    armc = as.numeric(input$muac),
    oedema = input$oedema
)

# Extract the relevant results
output <- result[1, c(
    "zwei",       # Weight-for-age
    "zlen",       # Height/length-for-age
    "zwfl",       # Weight-for-height/length
    "zac",        # MUAC-for-age
    "c9mo_flag",  # Measurement-position flag
    "fwei",
    "flen",
    "fwfl",
    "fac"
)]

# Return results as JSON
cat(toJSON(
    output,
    dataframe = "rows",
    auto_unbox = TRUE,
    na = "null"
))
