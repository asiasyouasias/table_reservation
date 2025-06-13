// src/pages/Login.jsx
import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
  try {
    // 기존 세션 정리
    await axios.post("/api/logout", {}, {
      withCredentials: true
    });
localStorage.removeItem("user");
    // 로그인 요청
    const res = await axios.post('/api/login', {
      email, password
    },{
      withCredentials: true
    });

    localStorage.setItem("user", JSON.stringify(res.data.user ?? { email }));

    // 새로고침으로 세션 반영 보장
    window.location.href = "/reservation";

  } catch (err) {
    if (err.response?.data?.message) {
      alert("로그인 실패: " + err.response.data.message);
    } else {
      alert("네트워크 오류 또는 알 수 없는 에러: " + err.message);
    }
  }
};

  return (

  <div className="login-container">
    <div className="login-box">
      <h2>로그인</h2>
      <input
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="비밀번호"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>로그인</button>
      <p>계정이 없으신가요? <a href="/signup">회원가입</a></p>
    </div>
  </div>
);
}