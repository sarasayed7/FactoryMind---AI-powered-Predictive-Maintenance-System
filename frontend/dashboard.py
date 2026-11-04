
import os

import pandas as pd
import requests
import streamlit as st


# -----------------------------------------
# 1. Page configuration
# -----------------------------------------

st.set_page_config(
    page_title="FactoryMind",
    page_icon="🏭",
    layout="wide"
)

API_BASE_URL = os.getenv(
    "FACTORYMIND_API_URL",
    "http://127.0.0.1:8000"
)


# -----------------------------------------
# 2. Reusable API request handler
# -----------------------------------------

def api_request(
    method,
    endpoint,
    payload=None,
    params=None,
    timeout=30
):
    try:
        with st.spinner("Processing request..."):
            response = requests.request(
                method=method,
                url=f"{API_BASE_URL}{endpoint}",
                json=payload,
                params=params,
                timeout=timeout
            )

            response.raise_for_status()
            return response.json()

    except requests.exceptions.Timeout:
        st.error("The request timed out. Please try again.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to FactoryMind API. "
            "Please check whether FastAPI is running."
        )

    except requests.exceptions.HTTPError:
        try:
            detail = response.json().get(
                "detail",
                response.text
            )
        except ValueError:
            detail = response.text

        st.error(
            f"API error ({response.status_code}): {detail}"
        )

    except requests.exceptions.RequestException as error:
        st.error(f"Request failed: {error}")

    except ValueError:
        st.error("The API returned an invalid JSON response.")

    return None


# -----------------------------------------
# 3. Application header and navigation
# -----------------------------------------

st.title("🏭 FactoryMind")
st.subheader("AI-Powered Industrial Maintenance Platform")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a feature",
    [
        "Overview",
        "Machine Assessment",
        "Machine History",
        "Maintenance Assistant"
    ]
)


# -----------------------------------------
# 4. Overview
# -----------------------------------------

if page == "Overview":

    st.header("Factory Overview")

    st.write(
        "Welcome to FactoryMind, your AI-powered industrial "
        "maintenance platform. Monitor machines, assess failure "
        "risk, and access maintenance guidance."
    )

    summary = api_request(
        "GET",
        "/dashboard/summary",
        timeout=10
    )

    if summary is not None:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Machines",
                summary["total_machines"]
            )

        with col2:
            st.metric(
                "Total Sensor Readings",
                summary["total_sensor_readings"]
            )

        with col3:
            st.metric(
                "Machines at Risk",
                summary["machines_at_risk"]
            )

    st.divider()

    st.subheader("Registered Machines")

    machines = api_request(
        "GET",
        "/machines",
        timeout=10
    )

    if machines is not None:

        if machines:
            st.dataframe(
                pd.DataFrame(machines),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No machines are currently registered.")


# -----------------------------------------
# 5. Machine Assessment
# -----------------------------------------

elif page == "Machine Assessment":

    st.header("Machine Risk Assessment")

    st.write(
        "Enter the latest sensor readings to assess machine failure risk."
    )

    machine_id = st.text_input(
        "Machine ID",
        value="M-101"
    )

    col1, col2 = st.columns(2)

    with col1:
        air_temperature = st.number_input(
            "Air Temperature (K)",
            value=300.0
        )

        process_temperature = st.number_input(
            "Process Temperature (K)",
            value=310.2
        )

        rotational_speed = st.number_input(
            "Rotational Speed (rpm)",
            value=1450,
            step=1
        )

    with col2:
        torque = st.number_input(
            "Torque (Nm)",
            value=45.3
        )

        tool_wear = st.number_input(
            "Tool Wear (min)",
            value=180,
            step=1
        )

    if st.button("Assess Machine", type="primary"):

        if not machine_id.strip():
            st.warning("Please enter a valid machine ID.")

        else:

            payload = {
                "machine_id": machine_id.strip(),
                "air_temperature": air_temperature,
                "process_temperature": process_temperature,
                "rotational_speed": rotational_speed,
                "torque": torque,
                "tool_wear": tool_wear
            }

            result = api_request(
                "POST",
                f"/machines/{machine_id.strip()}/assess",
                payload=payload,
                timeout=60
            )

            if result is not None:

                st.subheader("Assessment Results")

                failure_probability = result[
                    "failure_probability"
                ]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Machine ID",
                        result["machine_id"]
                    )

                with col2:
                    st.metric(
                        "Risk Status",
                        result["risk_status"]
                    )

                with col3:
                    st.metric(
                        "Failure Probability",
                        f"{failure_probability * 100:.1f}%"
                    )

                st.write(
                    f"Historical readings available: "
                    f"{result['history_count']}"
                )

                if result.get("maintenance_guidance"):

                    guidance = result["maintenance_guidance"]

                    st.divider()
                    st.subheader("Maintenance Recommendations")

                    st.write(guidance["answer"])

                    st.subheader("Supporting Sources")

                    st.json(guidance["sources"])


# -----------------------------------------
# 6. Machine History
# -----------------------------------------

elif page == "Machine History":

    st.header("Machine History")

    machine_id = st.text_input(
        "Machine ID",
        value="M-101",
        key="history_machine_id"
    )

    if st.button("Load History"):

        if not machine_id.strip():
            st.warning("Please enter a machine ID.")

        else:

            history = api_request(
                "GET",
                f"/machines/{machine_id.strip()}/history",
                params={
                    "limit": 20,
                    "offset": 0
                },
                timeout=15
            )

            if history is not None:

                if not history:
                    st.info("No historical readings found.")

                else:

                    rows = []

                    for reading in history:

                        sensor_data = {
                            "Reading ID": reading["id"],
                            "Timestamp": reading["recorded_at"],
                            "Air Temperature (K)": reading["air_temperature"],
                            "Process Temperature (K)": reading["process_temperature"],
                            "Rotational Speed (rpm)": reading["rotational_speed"],
                            "Torque (Nm)": reading["torque"],
                            "Tool Wear (min)": reading["tool_wear"]
                        }

                        predictions = reading.get("predictions") or [None]

                        for prediction in predictions:

                            if prediction is None:

                                prediction_data = {
                                    "Risk Status": None,
                                    "Failure Probability": None
                                }

                            else:

                                prediction_data = {
                                    "Risk Status": prediction["predicted_class"],
                                    "Failure Probability": prediction["failure_probability"]
                                }

                            rows.append({
                                **sensor_data,
                                **prediction_data
                            })

                    df = pd.DataFrame(rows)

                    st.subheader("Historical Sensor Readings")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # Failure probability trend

                    chart_df = df.dropna(
                        subset=["Failure Probability"]
                    ).copy()

                    if not chart_df.empty:

                        chart_df["Timestamp"] = pd.to_datetime(
                            chart_df["Timestamp"]
                        )

                        chart_df = chart_df.sort_values("Timestamp")

                        chart_df = chart_df.set_index("Timestamp")

                        chart_df["Failure Probability (%)"] = (
                            chart_df["Failure Probability"] * 100
                        )

                        st.divider()
                        st.subheader("Failure Probability Trend")

                        st.line_chart(
                            chart_df["Failure Probability (%)"]
                        )

                    else:
                        st.info(
                            "No prediction data is available "
                            "for these readings."
                        )


# -----------------------------------------
# 7. Maintenance Assistant
# -----------------------------------------

elif page == "Maintenance Assistant":

    st.header("Maintenance Assistant")

    st.write(
        "Ask questions about machine maintenance and troubleshooting."
    )

    question = st.text_area(
        "Enter your maintenance question:",
        placeholder="What maintenance inspections should be performed?"
    )

    if st.button("Ask FactoryMind", type="primary"):

        if not question.strip():

            st.warning("Please enter a maintenance question.")

        else:

            result = api_request(
                "POST",
                "/maintenance/ask",
                payload={
                    "question": question.strip()
                },
                timeout=60
            )

            if result is not None:

                st.subheader("Answer")

                st.write(result["answer"])

                st.divider()

                st.subheader("Supporting Sources")

                st.json(result["sources"])
