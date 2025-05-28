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
      const res = await axios.post('http://localhost:5000/api/login', {
        email, password
      });
      if (res.data.success) {
        localStorage.setItem("user", JSON.stringify(res.data.user));
        navigate("/reservation");
      } else {
        alert("로그인 실패: " + res.data.message);
      }
    } catch (err) {
      alert("에러 발생: " + err.message);
    }
  };

  return (
    <div className='App'>
      <h2>로그인</h2>
      <input placeholder="이메일" onChange={(e) => setEmail(e.target.value)} />
      <input type="password" placeholder="비밀번호" onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleLogin}>로그인</button>
      <p>계정이 없으신가요? <a href="/signup">회원가입</a></p>
    </div>
  );
}
