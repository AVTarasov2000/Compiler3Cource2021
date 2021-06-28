from task1.CompilerDemoPyparsing.compiler_demo import program


def main() -> None:

    prog1 = '''
        int input_int(string name) {
            if (name != "") {
                print("Введите " + name + ": ");
            }
            return to_int(read());
        }
        float input_float(string name) {
            if (name != "") {
                print("Введите " + name + ": ");
            }
            return to_float(read());
        }

        int g, g2 = g, g4 = 90;

        int a = input_int("a");
        float b = input_float("b"), c = input_float("c");  /* comment 1
        int d = input_int("d");
        */
        for (int i = 0, j = 8; ((i <= 5)) && g; i = i + 1, print(5))
            for(; a < b;)
                if (a > 7 + b) {
                    c = a + b * (2 - 1) + 0;  // comment 2
                    string bb = "98\tура";
                }
                else if (a)
                    print((c + 1) + " " + 89.89);
        for(bool i = true;;);

        int z;
        z=0;
    '''
    prog2 = 'int f1(int p1, float p2) { string a = p1 + p2; int x; }'''
    prog3 = 'for (;;);'
    prog4 = 'int i; i = 5;'
    prog5 = '''
        int input_int(string name) {
            if (name != "") {
                print("Введите " + name + ": ");
            }
            return to_int(read());

            // bool a() { }
        }
        int input_int2(string name, int a, int name2) {
            if (name != "") {
                print("Введите " + name + ": ");
            }
            return "";
        }
    
    '''
    test1 = '''private class A{
    {
        await b();
        int a = 1+2+b().a.b();
        a = 1;
    }
    async int a(int b){
        int a = a().b.c().c.v();
        int a = await a();
        a();
    }
    public class A{
    class A{
    int a = 0, b = a, c;
    String a = 0, b = a, c;
    }
    }
    }
    }
    class B{
    int a = 0, b = a, c;
    String a = 0, b = a, c;
    }'''

    # int g;
    #  public void calk(Integer c){
    #     int a;
    #     a = await func(c, n, d);
    #     int w = await func(d, g, h);
    #     c = a;
    #     return c;
    #    }
    # for (int i; i < a; i++){
    #      int a = i;
    # }
    test = '''public class Test {
    public static void main() {
        Date date = Date();
        String str = "Hello";
        StringBuilder sb = StringBuilder();
    
        Integer i = await test(Factorial());
        await sb.toString();
        System.out.println(i);
        System.out.println(Date().getTime() - date.getTime());
    }

    async public static void test(String x){
        System.out.println(x);
    }

    async public static Integer Factorial()
    {
        int result = 1;
        for(int i = 1; i <= 9; i = i + 1)
        {
            result = result * i;
        }

        return result;
    }
}'''

    program.execute(test)


if __name__ == "__main__":
    main()
