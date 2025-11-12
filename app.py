import streamlit as st
import pandas as pd
from io import BytesIO

# Alap beállítások
st.set_page_config(page_title="TPRO - Multi Account Checker", page_icon="🔍")

st.title("🔍 TPRO - Multi Account Checker")

st.markdown("### 1️⃣ Töltsd fel a **korábban törölt játékosok adatait tartalmazó .csv fájlt** (DataMatrix-USZ_deleted_request_by_player riport)")

deleted_file = st.file_uploader("Korábban töröltek CSV feltöltése", type="csv")

if deleted_file:
    try:
        deleted_df = pd.read_csv(deleted_file, sep=None, engine="python")
        # Oszlopnevek kisbetűsítése az egységesség miatt
        deleted_df.columns = deleted_df.columns.str.strip().str.lower()

        if "personal id" not in deleted_df.columns:
            st.error("❌ A feltöltött fájlban nincs 'Personal ID' oszlop.")
        elif "user id" not in deleted_df.columns:
            st.error("❌ A feltöltött fájlban nincs 'User ID' oszlop.")
        else:
            # Adattisztítás
            deleted_df["personal id"] = (
                deleted_df["personal id"]
                .astype(str)
                .str.replace(r"_adatved|_adatve|_adatv", "", regex=True)
                .str.strip()
            )

            st.success("✅ A korábban törölt játékosok adatai sikeresen beolvasva és megtisztítva.")

            st.markdown("### 2️⃣ Töltsd fel a **tegnap regisztráltak** adatait tartalmazó .csv fájlt (DataMatrix-Reg_yesterday)")

            new_file = st.file_uploader("Tegnap regisztráltak CSV feltöltése", type="csv")

            if new_file:
                try:
                    new_df = pd.read_csv(new_file, sep=None, engine="python")
                    new_df.columns = new_df.columns.str.strip().str.lower()

                    if "personal id" not in new_df.columns or "user id" not in new_df.columns:
                        st.error("❌ A második fájlban nincs megfelelő 'Personal ID' vagy 'User ID' oszlop.")
                    else:
                        # Új regisztrációk száma
                        total_new = new_df["personal id"].nunique()

                        # Azonosítók tisztítása
                        new_df["personal id"] = (
                            new_df["personal id"].astype(str).str.strip()
                        )

                        # Egyezések keresése
                        matches = new_df[new_df["personal id"].isin(deleted_df["personal id"])]

                        # Összekapcsolás a régi User ID-kkal
                        merged = pd.merge(
                            matches,
                            deleted_df[["personal id", "user id"]],
                            on="personal id",
                            how="left",
                            suffixes=("_new", "_old")
                        )

                        # Ha több régi User ID is volt, csoportosítjuk
                        merged_grouped = (
                            merged.groupby(["personal id", "user id_new"], as_index=False)
                            .agg({"user id_old": lambda x: ", ".join(x.astype(str).unique())})
                        )

                        # Találatok száma
                        match_count = len(merged_grouped)

                        # Eredmények megjelenítése
                        st.success(f"📊 Új regisztrációk száma: **{total_new}**")
                        st.warning(f"⚠️ Új regisztrációk között a korábban töröltek között megtalálható: **{match_count}**")

                        st.markdown("### 📋 Többszörös regisztrációk")
                        st.dataframe(merged_grouped)

                        # Excel export
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            merged_grouped.to_excel(writer, index=False, sheet_name="Találatok")

                        st.download_button(
                            label="💾 Eredmények letöltése Excel formátumban",
                            data=output.getvalue(),
                            file_name="multi_account_check_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                except Exception as e:
                    st.error(f"Hiba történt a második fájl feldolgozásakor: {e}")

    except Exception as e:
        st.error(f"Hiba történt az első fájl feldolgozásakor: {e}")








