package googleapi
import("testing";"time";"net/http";"net/http/httptest")
func TestEdithHeaderTimeout(t *testing.T){if newBaseTransport().ResponseHeaderTimeout != 120*time.Second {t.Fatal("wrong header timeout")}}
func TestEdithSlowResponse(t *testing.T){
 s:=httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter,r *http.Request){time.Sleep(31*time.Second);w.WriteHeader(200)}));defer s.Close()
 c:=NewBoundedHTTPClient();r,e:=c.Get(s.URL);if e!=nil{t.Fatal(e)};defer r.Body.Close();if r.StatusCode!=200{t.Fatal(r.StatusCode)}
}
