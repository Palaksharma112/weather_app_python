import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

from auth import signup, login
import plotly.express as px


if not os.path.exists("weather_data.xlsx"):

    df = pd.DataFrame(columns=[
        "Date",
        "Time",
        "City",
        "Temperature",
        "Humidity",
        "Pressure",
        "Wind Speed",
        "Weather"
    ])

    df.to_excel("weather_data.xlsx", index=False)

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(
    page_title="Weather Analytics",
    page_icon="🌦",
    layout="wide"
)

API_KEY = "59eea54d1b18d3b7db904628cda7c0f7"

# ===========================
# SESSION STATE
# ===========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ===========================
# WEATHER FUNCTION
# ===========================
def get_weather(city):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city.strip(),
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    print(response.status_code)
    print(response.text)

    if response.status_code == 200:
        return response.json()

    return None


def get_forecast(city):

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city.strip(),
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

    return None



# ===========================
# SAVE TO EXCEL
# ===========================
def save_to_excel(weather):

    file_name = "weather_data.xlsx"

    columns = [
        "Date",
        "Time",
        "City",
        "Temperature",
        "Humidity",
        "Pressure",
        "Wind Speed",
        "Weather"
    ]

    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
    else:
        df = pd.DataFrame(columns=columns)

    df = pd.concat([df, pd.DataFrame([weather])], ignore_index=True)

    df.to_excel(file_name, index=False)

# ===========================
# SIDEBAR
# ===========================

st.sidebar.title("🌦 Weather App")

if not st.session_state.logged_in:

    menu = st.sidebar.selectbox(
        "Choose Option",
        ["Login", "Signup"]
    )


# ===========================
# SIGNUP
# ===========================

# ---------------- Signup ----------------
    if menu == "Signup":

        st.title("📝 Create Account")

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up", key="signup_btn"):

            if signup(name, email, password):
                st.success("Account created successfully.")
            else:
                st.error("Email already exists.")

    # ---------------- Login ----------------
    else:

        st.title("🔐 Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="login_btn"):

            user = login(email, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[1]
                st.rerun()
            else:
                st.error("Invalid Email or Password")

# -------------------------------------------------
# SHOW DASHBOARD ONLY AFTER LOGIN
# -------------------------------------------------
else:

    st.sidebar.success(f"Welcome {st.session_state.username}")

    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("🌦 Weather Analytics Dashboard")
    st.write("Search any city to view live weather information.")

    city = st.text_input(
        "Enter City Name",
        placeholder="Example: Jaipur"
    )

    if st.button("🔍 Get Weather", key="weather_btn"):

        if city.strip() == "":
            st.warning("Please enter a city name.")

        else:

            data = get_weather(city)

            if data:

                temperature = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                pressure = data["main"]["pressure"]
                wind = data["wind"]["speed"]
                weather = data["weather"][0]["description"]

                sunrise = datetime.fromtimestamp(
                    data["sys"]["sunrise"]
                ).strftime("%H:%M:%S")

                weather_record = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "City": city.title(),
                    "Temperature": temperature,
                    "Humidity": humidity,
                    "Pressure": pressure,
                    "Wind Speed": wind,
                    "Weather": weather
                }

                save_to_excel(weather_record)

                st.success("Weather data saved successfully!")

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("🌡 Temperature", f"{temperature} °C")
                    st.metric("💧 Humidity", f"{humidity}%")

                with c2:
                    st.metric("🌬 Wind Speed", f"{wind} m/s")
                    st.metric("🌍 Pressure", f"{pressure} hPa")

                with c3:
                    st.metric("☁ Weather", weather.title())
                    st.metric("🌅 Sunrise", sunrise)

                    # ===========================
                    # Tomorrow Weather Forecast
                    # ===========================

                forecast = get_forecast(city)

                if forecast:

                        st.divider()
                        st.subheader("🌤 Tomorrow Weather Forecast")

                        # Around 24 hours later
                        tomorrow = forecast["list"][7]

                        t_temp = tomorrow["main"]["temp"]
                        t_humidity = tomorrow["main"]["humidity"]
                        t_pressure = tomorrow["main"]["pressure"]
                        t_wind = tomorrow["wind"]["speed"]
                        t_weather = tomorrow["weather"][0]["description"]
                        from datetime import datetime

                        t_time = datetime.strptime(
                                     tomorrow["dt_txt"],
                                     "%Y-%m-%d %H:%M:%S"
                                     ).strftime("%I:%M %p")

                    

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("🌡 Temperature", f"{t_temp} °C")
                            st.metric("💧 Humidity", f"{t_humidity}%")

                        with col2:
                            st.metric("🌬 Wind Speed", f"{t_wind} m/s")
                            st.metric("🌍 Pressure", f"{t_pressure} hPa")

                        with col3:
                            st.metric("☁ Weather", t_weather.title())
                            st.metric("sunrise",f" {t_time}")

            else: 
                                    st.error("City not found.")




    st.divider()

    st.subheader("📁 Weather Dataset")

    if os.path.exists("weather_data.xlsx"):

        df = pd.read_excel("weather_data.xlsx")

        st.dataframe(df, use_container_width=True)

        with open("weather_data.xlsx", "rb") as file:

            st.download_button(
                label="📥 Download Weather Dataset",
                data=file,
                file_name="weather_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:

        st.info("No weather data available.")

    st.divider()
 
    st.subheader("📈 Temperature Trend")

    df = pd.read_excel("weather_data.xlsx")

    fig = px.line(
    df,
    x="Date",
    y="Temperature",
    markers=True,
    title="Temperature Trend"
)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💧 Humidity Trend")

    fig = px.bar(
    df,
    x="City",
    y="Humidity",
    color="Humidity",
    title="Humidity by City"
)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌍 Pressure Trend")

    fig = px.area(
    df,
    x="Date",
    y="Pressure"
)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("☁ Weather Distribution")

    fig = px.pie(
    df,
    names="Weather",
    title="Weather Conditions"
)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌬 Wind Speed")

    fig = px.scatter(
    df,
    x="City",
    y="Wind Speed",
    size="Wind Speed",
    color="Temperature"
)

    st.plotly_chart(fig, use_container_width=True)    