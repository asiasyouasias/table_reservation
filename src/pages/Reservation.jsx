import { useState,useEffect } from "react";
import axios from "axios";

export default function Reservation() {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("lunch");
  const [tables, setTables] = useState([]);

  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setDate(tomorrow.toISOString().split('T')[0]);
  }, []);

  const [selectedTable, setSelectedTable] = useState(null);
  const [showPopup, setShowPopup] = useState(false);

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [guestCount, setGuestCount] = useState(1);

  const today = new Date();
  today.setDate(today.getDate() + 1);
  const minDate = today.toISOString().split('T')[0];

  //   const handleSearch = async () => {
  //   // 여기에 await 가능!
  //   try {
  //     const res = await axios.get('http://localhost:5000/api/tables', {
  //       params: { date, time },
  //     });
  //     setTables(res.data.tables);
  //   } catch (err) {
  //     alert("테이블 불러오기 실패");
  //   }
  // };
  const handleSearch = async () => {
    if (!date) {
      alert("날짜를 선택하세요.");
      return;
    }

    // ✅ 날짜 제한 검사 추가
    const selected = new Date(date);
    const maxDate = new Date();

    today.setHours(0, 0, 0, 0);
    selected.setHours(0, 0, 0, 0);
    maxDate.setDate(today.getDate() + 30);

    if (selected < today) {
      alert("이전 날짜는 선택할 수 없습니다.");
      return;
    }

    if (selected.getTime() === today.getTime()) {
      alert("당일 예약은 불가합니다.");
      return;
    }

    if (selected > maxDate) {
      alert("30일 이내 날짜만 예약할 수 있습니다.");
      return;
    }
    // 💡 여기 axios 대신 가짜 데이터!
    const fakeTables = [
      { id: 1, location: "창가", capacity: 2 },
      { id: 2, location: "룸", capacity: 4 },
      { id: 3, location: "내부", capacity: 6 },
    ];
    setTables(fakeTables);
  };

  const handleReserve = async () => {
    const user = JSON.parse(localStorage.getItem("user")); // or 생략

    try {
      const res = await axios.post("http://localhost:5000/api/reservations", {
        tableId: selectedTable.id,
        date,
        time,
        name,
        phone,
        cardNumber,
        guestCount,
      });
      alert("예약 성공!");
      setShowPopup(false);
    } catch (err) {
      alert("예약 실패!");
    }
  };

  return (
    <div className="App">
      <h2>테이블 예약</h2>
      <input
        type="date"
        min={minDate}
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />
      <select onChange={(e) => setTime(e.target.value)} value={time}>
        <option value="lunch">점심</option>
        <option value="dinner">저녁</option>
      </select>
      <button onClick={handleSearch}>테이블 보기</button>

      <div style={{ marginTop: "2rem" }}>
        {tables.length === 0 ? (
          <p>테이블이 없습니다.</p>
        ) : (
          tables.map((table) => (
            <div
              key={table.id}
              style={{
                border: "1px solid #444",
                padding: "1rem",
                marginBottom: "1rem",
                borderRadius: "8px",
                cursor: "pointer",
              }}
              onClick={() => {
                setSelectedTable(table);
                setGuestCount(1);
                setShowPopup(true);
              }}
            >
              <p>위치: {table.location}</p>
              <p>인원: {table.capacity}명</p>
            </div>
          ))
        )}
      </div>

      {/* 팝업 창 */}
      {showPopup && selectedTable && (
        <div className="popup-overlay">
          <div className="popup">
            <h3>{selectedTable.location} 테이블 예약</h3>
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
              min={1}
              max={selectedTable.capacity}
            />

            <button onClick={handleReserve}>예약하기</button>
            <button onClick={() => setShowPopup(false)}>닫기</button>
          </div>
        </div>
      )}
    </div>
  );
}
