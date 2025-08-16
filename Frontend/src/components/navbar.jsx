import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { logout } from "../state/authSlice";

function Navbar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <nav className="sticky top-0 z-50 w-full flex items-center justify-between bg-white border-gray-200  p-4 shadow-sm">
      <div> </div>
      <div>
        <span className="font-bold text-lg text-blue-400 tracking-tight">
          Text-Summerizer
        </span>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={handleLogout}
          className="text-blue-600 hover:text-blue-800 font-semibold cursor-pointer"
        >
          LogOut
        </button>
        {user && (
          <span className="text-sm text-blue-600 font-semibold text-capitalize border bg-gray-100 rounded-full p-1 w-8 h-8 flex items-center justify-center">
            {(user.username.slice(0, 1).toUpperCase() || user.email)
              .slice(0, 1)
              .toUpperCase()}
          </span>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
