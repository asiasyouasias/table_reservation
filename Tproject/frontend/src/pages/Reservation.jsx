import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Reservation() {
  const [date, setDate] = useState("");
  const [meal, setTime] = useState("lunch");
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [guestCount, setGuestCount] = useState(1);
  const navigate = useNavigate();
  const translateLocation = (location) => {
  switch (location) {
    case "window":
      return "창가";
    case "room":
      return "방";
    case "inside":
      return "내부";
    default:
      return location; 
  }
};


  const handleLogout = async () => {
    try {
      await axios.post(
        "/api/logout",
        {},
        {
          withCredentials: true,
        }
      );
      alert("로그아웃 되었습니다.");
      navigate("/"); // 또는 "/login"
    } catch (err) {
      alert("로그아웃 실패: " + err.message);
    }
  };

  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate());
    setDate(tomorrow.toISOString().split("T")[0]);
  }, []);

  const today = new Date();
  today.setDate(today.getDate());
  const minDate = today.toISOString().split("T")[0];

  const selected = new Date(date);
    const maxDate = new Date();
    today.setHours(0, 0, 0, 0);
    selected.setHours(0, 0, 0, 0);
    maxDate.setDate(today.getDate() + 30);


  const handleSearch = async () => {
    if (!date) {
      alert("날짜를 선택하세요.");
      return;
    }

    if (selected < today) {
      alert("이전 날짜는 선택할 수 없습니다.");
      setTables([]);
      return;
    }

    if (selected.getTime() === today.getTime()) {
      alert("당일 예약 또는 취소가 불가합니다.");
    }

    if (selected > maxDate) {
      alert("30일 이내 날짜만 예약할 수 있습니다.");
      setTables([]);
      return;
    }

    try {
      const res = await axios.get("/api/tables", {
        params: { date, meal },
        withCredentials: true,
      });
      setTables(res.data); 
    } catch (err) {
      console.error("에러:", err.response?.data || err.message);
      alert("테이블 불러오기 실패");
      setTables([]);
    }
  };

  const handleReserve = async () => {
    if (selected > maxDate) {
      alert("30일 이내 날짜만 예약할 수 있습니다.");
      return;
    }

    try {
      const res = await axios.post(
        "/api/reservations",
        {
          table_id: selectedTable.id,
          date,
          meal,
          name,
          phone,
          credit: cardNumber,
          quantity: guestCount,
        },
        {
          withCredentials: true, 
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      
      alert("예약 성공!");
      setShowPopup(false);
      handleSearch();
    } catch (err) {
      console.error("예약 실패:", err.response?.data || err.message);
      alert("예약 실패: " + (err.response?.data?.message || err.message));
    }
  };
  const cancelReservation = async (tableId) => {
  try {
    const res = await axios.post("/api/reservations/cancel", {
      table_id: tableId,
      date,
      meal,
    }, {
      withCredentials: true,
    });

    if (res.data.success) {
      alert("예약이 취소되었습니다.");
      handleSearch();
    }
  } catch (e) {
    alert("예약 취소 실패: " + (e.response?.data?.message || e.message));
  }
};


  return (
    <div className="App">
      <h2>테이블 예약</h2>
      <div style={{ position: "absolute", top: "20px", right: "20px" }}>
        <button onClick={handleLogout}>로그아웃</button>
      </div>
      <input
        type="date"
        min={minDate}
        value={date}
        onChange={(e) => setDate(e.target.value)}
        onKeyDown={(e) => e.preventDefault()}
      />
      <select onChange={(e) => setTime(e.target.value)} value={meal}>
        <option value="lunch">점심</option>
        <option value="dinner">저녁</option>
      </select>
      <button onClick={handleSearch}>테이블 보기</button>

      <div style={{ marginTop: "2rem" }}>
        {tables.length === 0 ? (
          <p>테이블이 없습니다.</p>
        ) : (
          tables.map((table) => {
            let bgColor = "#1e1e1e"; // 기본: 예약 가능
            let textColor = "#f1f1f1";

            if (table.is_reserved) {
              if (table.is_mine) {
                bgColor = "#2a9d8f"; // 내 예약: 청록색
              } else {
                bgColor = "#3a3a3a"; // 남의 예약: 회색
                textColor = "#aaaaaa";
              }
            }

            return (
              <div
                key={table.id}
                style={{
                  backgroundColor: bgColor,
                  color: textColor,
                  border: "1px solid #444",
                  padding: "1rem",
                  marginBottom: "1rem",
                  borderRadius: "8px",
                  cursor:
                    table.is_reserved && !table.is_mine
                      ? "not-allowed"
                      : "pointer",
                  opacity: table.is_reserved && !table.is_mine ? 0.7 : 1,
                  transition: "all 0.3s",
                }}
                onClick={() => {
                  const isToday = new Date(date).toDateString() === new Date().toDateString();

                  if (table.is_reserved && !table.is_mine) {
                    alert("이미 예약된 테이블입니다.");
                    return;
                  }

                  if (table.is_reserved && table.is_mine) {
                    if (isToday) {
                      alert("당일 예약은 취소할 수 없습니다.");
                      return;
                    }
                    const confirmed = window.confirm("해당 예약을 취소하시겠습니까?");
                    if (confirmed) cancelReservation(table.id);
                    return;
                  }

                  if (isToday) {
                    alert("당일 예약은 불가합니다.");
                    return;
                    }

                  setSelectedTable(table);
                  setGuestCount(1);
                  setShowPopup(true);
                }}
              >
                <p>위치: {translateLocation(table.location)}</p>
                <p>인원: {table.capacity}명</p>
                {table.is_reserved && (
                  <p style={{ fontStyle: "italic" }}>
                    {table.is_mine ? "내 예약" : "예약됨"}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>

      {showPopup && selectedTable && (
        <div className="popup-overlay">
          <div className="popup">
            <h3> [{meal === "lunch" ? "점심" : "저녁"}] {translateLocation(selectedTable.location)} 테이블 예약</h3>
            <p>최대 수용 인원: {selectedTable.capacity}명</p>

            <input
              type="text"
              placeholder="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <input
              type="tel"
              placeholder="전화번호"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <input
              type="text"
              placeholder="카드번호"
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
            />
            <input
              type="number"
              placeholder="인원 수"
              value={guestCount}
              onChange={(e) => setGuestCount(Number(e.target.value))}
              min={0}
            />

            <button onClick={handleReserve}>예약하기</button>
            <button onClick={() => setShowPopup(false)}>닫기</button>
          </div>
        </div>
      )}
    </div>
  );
}
